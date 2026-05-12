from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.processed_dataset import ProcessedDataset
from app.models.uploaded_file import UploadedFile

# ── Load embedding model once at startup ─────────────────────────────
# all-MiniLM-L6-v2 produces 384-dim vectors, fast and accurate
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ── Pinecone client ──────────────────────────────────────────────────
def get_pinecone_index():
    pc    = Pinecone(api_key=settings.PINECONE_API_KEY)
    index = pc.Index(settings.PINECONE_INDEX_NAME)
    return index


# ── Build human-readable text chunks from KPI data ───────────────────
def build_text_chunks(
    processed : ProcessedDataset,
    file_record: UploadedFile
) -> list[dict]:
    """
    Convert structured KPI data into text summaries.
    Each chunk = one vector in Pinecone.
    Returns list of {id, text, metadata} dicts.
    """
    chunks  = []
    kpis    = processed.kpi_summary or {}
    file_id = processed.file_id
    user_id = file_record.user_id
    ftype   = file_record.file_type

    # ── Chunk 1: Overall KPI summary ──
    kpi_text = (
        f"Business file type: {ftype}. "
        f"Total records: {kpis.get('total_rows', 'N/A')}. "
        f"Total amount ({kpis.get('amount_column_used','revenue')}): "
        f"{kpis.get('total_amount', 'N/A')}. "
        f"Average amount: {kpis.get('average_amount', 'N/A')}. "
        f"Maximum: {kpis.get('max_amount', 'N/A')}. "
        f"Minimum: {kpis.get('min_amount', 'N/A')}. "
        f"Unique stores: {kpis.get('unique_stores', 'N/A')}. "
        f"Unique customers: {kpis.get('unique_customers', 'N/A')}. "
        f"Top category: {kpis.get('top_category', 'N/A')}."
    )
    chunks.append({
        "id"      : f"file_{file_id}_kpi_overall",
        "text"    : kpi_text,
        "metadata": {
            "file_id"   : file_id,
            "user_id"   : user_id,
            "file_type" : ftype,
            "chunk_type": "kpi_overall",
        }
    })

    # ── Chunk 2: Data quality summary ──
    missing  = processed.missing_values    or {}
    outliers = processed.outliers_detected or {}

    quality_text = (
        f"Data quality report for {ftype} file. "
        f"Total rows after cleaning: {processed.total_rows}. "
        f"Duplicates removed: {processed.duplicate_count}. "
        f"Columns with missing values: "
        f"{', '.join(missing.keys()) if missing else 'none'}. "
        f"Columns with outliers: "
        f"{', '.join(f'{k}({v})' for k,v in outliers.items()) if outliers else 'none'}."
    )
    chunks.append({
        "id"      : f"file_{file_id}_quality",
        "text"    : quality_text,
        "metadata": {
            "file_id"   : file_id,
            "user_id"   : user_id,
            "file_type" : ftype,
            "chunk_type": "data_quality",
        }
    })

    # ── Chunk 3+: Monthly trend (one chunk per month) ──
    monthly_trend = kpis.get("monthly_trend", [])
    for entry in monthly_trend:
        month = entry.get("month", "unknown")
        value = entry.get("value", 0)

        month_text = (
            f"{ftype.capitalize()} data for {month}: "
            f"total {kpis.get('amount_column_used','amount')} = {value:,.2f}."
        )
        chunks.append({
            "id"      : f"file_{file_id}_month_{month}",
            "text"    : month_text,
            "metadata": {
                "file_id"   : file_id,
                "user_id"   : user_id,
                "file_type" : ftype,
                "chunk_type": "monthly_trend",
                "period"    : month,
                "value"     : float(value),
            }
        })

    # ── Chunk 4: Additional metrics ──
    additional = kpis.get("additional_metrics", {})
    if additional:
        metrics_text = f"Additional metrics for {ftype} file: "
        parts = []
        for col, stats in additional.items():
            parts.append(
                f"{col} (mean={stats['mean']}, "
                f"min={stats['min']}, max={stats['max']})"
            )
        metrics_text += "; ".join(parts) + "."

        chunks.append({
            "id"      : f"file_{file_id}_metrics",
            "text"    : metrics_text,
            "metadata": {
                "file_id"   : file_id,
                "user_id"   : user_id,
                "file_type" : ftype,
                "chunk_type": "additional_metrics",
            }
        })

    return chunks


# ── Embed and upsert to Pinecone ─────────────────────────────────────
def embed_and_store(
    db     : Session,
    file_id: int
) -> dict:
    """
    Main function:
    1. Load processed dataset from DB
    2. Build text chunks
    3. Embed with sentence-transformers
    4. Upsert vectors to Pinecone
    """

    # Load records
    processed = db.query(ProcessedDataset).filter(
        ProcessedDataset.file_id == file_id
    ).first()

    if not processed:
        raise ValueError(
            f"No processed dataset found for file_id {file_id}. "
            f"Run preprocessing first."
        )

    file_record = db.query(UploadedFile).filter(
        UploadedFile.id == file_id
    ).first()

    # Build text chunks
    chunks = build_text_chunks(processed, file_record)

    # Embed all texts at once (batch = fast)
    texts    = [c["text"] for c in chunks]
    vectors  = embedding_model.encode(texts, show_progress_bar=False)

    # Build Pinecone upsert payload
    upsert_data = []
    for chunk, vector in zip(chunks, vectors):
        upsert_data.append({
            "id"      : chunk["id"],
            "values"  : vector.tolist(),
            "metadata": chunk["metadata"],
        })

    # Upsert to Pinecone
    index = get_pinecone_index()
    index.upsert(vectors=upsert_data)

    return {
        "file_id"      : file_id,
        "chunks_stored": len(chunks),
        "vector_dim"   : len(vectors[0]),
        "chunk_ids"    : [c["id"] for c in chunks],
    }


# ── Search Pinecone (used by RAG later) ──────────────────────────────
def search_similar_chunks(
    query  : str,
    user_id: int,
    file_id: int = None,
    top_k  : int = 5
) -> list[dict]:
    """
    Convert a question into a vector and find
    the most relevant chunks in Pinecone.
    Used by the RAG/AI module.
    """

    # Embed the query
    query_vector = embedding_model.encode([query])[0].tolist()

    # Build filter — only return chunks for this user
    pinecone_filter = {"user_id": {"$eq": user_id}}
    if file_id:
        pinecone_filter["file_id"] = {"$eq": file_id}

    # Search
    index   = get_pinecone_index()
    results = index.query(
        vector         = query_vector,
        top_k          = top_k,
        include_metadata = True,
        filter         = pinecone_filter,
    )

    # Return clean list
    matches = []
    for match in results["matches"]:
        matches.append({
            "score"     : round(match["score"], 4),
            "chunk_id"  : match["id"],
            "chunk_type": match["metadata"].get("chunk_type"),
            "period"    : match["metadata"].get("period"),
            "file_id"   : match["metadata"].get("file_id"),
        })

    return matches