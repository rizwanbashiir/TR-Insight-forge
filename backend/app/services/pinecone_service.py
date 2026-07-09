from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from beanie import PydanticObjectId
from typing import Union, List

from app.config.settings import settings
from app.models.processed_dataset import ProcessedDataset
from app.models.uploaded_file import UploadedFile

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def get_pinecone_index():
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    index = pc.Index(settings.PINECONE_INDEX_NAME)
    return index


def build_text_chunks(
    processed: ProcessedDataset,
    file_record: UploadedFile
) -> list[dict]:
    chunks = []
    kpis = processed.kpi_summary or {}
    file_id_str = str(processed.file_id)
    user_id_str = str(file_record.user_id)
    ftype = file_record.file_type

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
        "id": f"file_{file_id_str}_kpi_overall",
        "text": kpi_text,
        "metadata": {
            "file_id": file_id_str,
            "user_id": user_id_str,
            "file_type": str(ftype),
            "chunk_type": "kpi_overall",
            "text": kpi_text,
        }
    })

    missing = processed.missing_values or {}
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
        "id": f"file_{file_id_str}_quality",
        "text": quality_text,
        "metadata": {
            "file_id": file_id_str,
            "user_id": user_id_str,
            "file_type": str(ftype),
            "chunk_type": "data_quality",
            "text": quality_text,
        }
    })

    monthly_trend = kpis.get("monthly_trend", [])
    for entry in monthly_trend:
        month = entry.get("month", "unknown")
        value = entry.get("value", 0)

        month_text = (
            f"{ftype.capitalize()} data for {month}: "
            f"total {kpis.get('amount_column_used','amount')} = {value:,.2f}."
        )
        chunks.append({
            "id": f"file_{file_id_str}_month_{month}",
            "text": month_text,
            "metadata": {
                "file_id": file_id_str,
                "user_id": user_id_str,
                "file_type": str(ftype),
                "chunk_type": "monthly_trend",
                "period": str(month),
                "value": float(value),
                "text": month_text,
            }
        })

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
            "id": f"file_{file_id_str}_metrics",
            "text": metrics_text,
            "metadata": {
                "file_id": file_id_str,
                "user_id": user_id_str,
                "file_type": str(ftype),
                "chunk_type": "additional_metrics",
                "text": metrics_text,
            }
        })

    return chunks


async def embed_and_store(db, file_id) -> dict:
    oid = PydanticObjectId(file_id) if isinstance(file_id, str) else file_id

    processed = await ProcessedDataset.find_one(ProcessedDataset.file_id == oid)
    if not processed:
        raise ValueError(
            f"No processed dataset found for file_id {file_id}. "
            f"Run preprocessing first."
        )

    file_record = await UploadedFile.get(oid)

    chunks = build_text_chunks(processed, file_record)

    texts = [c["text"] for c in chunks]
    vectors = embedding_model.encode(texts, show_progress_bar=False)

    upsert_data = []
    for chunk, vector in zip(chunks, vectors):
        upsert_data.append({
            "id": chunk["id"],
            "values": vector.tolist(),
            "metadata": chunk["metadata"],
        })

    index = get_pinecone_index()
    index.upsert(vectors=upsert_data)

    return {
        "file_id": str(file_id),
        "chunks_stored": len(chunks),
        "vector_dim": len(vectors[0]),
        "chunk_ids": [c["id"] for c in chunks],
    }


def search_similar_chunks(
    query: str,
    user_id: str,
    file_ids: Union[str, List[str]] = None,
    top_k: int = 5
) -> list[dict]:
    query_vector = embedding_model.encode([query])[0].tolist()

    pinecone_filter = {}
    if file_ids is not None:
        if isinstance(file_ids, list):
            fids = [str(fid) for fid in file_ids]
            if len(fids) == 1:
                pinecone_filter["file_id"] = {"$eq": fids[0]}
            elif len(fids) > 1:
                pinecone_filter["file_id"] = {"$in": fids}
        else:
            pinecone_filter["file_id"] = {"$eq": str(file_ids)}

    index = get_pinecone_index()
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
        filter=pinecone_filter,
    )

    matches = []
    for match in results["matches"]:
        matches.append({
            "score": round(match["score"], 4),
            "chunk_id": match["id"],
            "chunk_type": match["metadata"].get("chunk_type"),
            "period": match["metadata"].get("period"),
            "file_id": match["metadata"].get("file_id"),
            "text": match["metadata"].get("text", ""),
        })

    return matches