from sqlalchemy.orm import Session

from app.models.ai_insight import AiInsight
from app.models.processed_dataset import ProcessedDataset
from app.models.uploaded_file import UploadedFile
from app.services.pinecone_service import search_similar_chunks
from app.services.prompt_builder import build_rag_prompt
from app.services.prompt_builder import build_general_insights_prompt
from app.services.ollama_service import call_ollama


from typing import Union, List

def merge_kpi_summaries(summaries: List[dict]) -> dict:
    if not summaries:
        return {}
    if len(summaries) == 1:
        return summaries[0]

    merged = {
        "file_type": summaries[0].get("file_type", "business"),
        "total_amount": 0.0,
        "average_amount": 0.0,
        "max_amount": 0.0,
        "min_amount": float("inf"),
        "unique_customers": 0,
        "unique_stores": 0,
        "total_orders": 0,
        "top_category": "N/A",
        "monthly_trend": []
    }

    category_counts = {}
    monthly_map = {}
    avg_sums = 0.0
    avg_count = 0

    for s in summaries:
        merged["total_amount"] += float(s.get("total_amount") or 0)
        
        if "average_amount" in s:
            avg_sums += float(s["average_amount"])
            avg_count += 1
            
        merged["max_amount"] = max(merged["max_amount"], float(s.get("max_amount") or 0))
        if "min_amount" in s:
            merged["min_amount"] = min(merged["min_amount"], float(s.get("min_amount") or 0))
            
        merged["total_orders"] += int(s.get("total_orders") or 0)
        
        cat = s.get("top_category")
        if cat and cat != "N/A":
            category_counts[cat] = category_counts.get(cat, 0) + 1
            
        for m in s.get("monthly_trend") or []:
            month = m.get("month")
            val = float(m.get("value") or 0)
            if month:
                monthly_map[month] = monthly_map.get(month, 0.0) + val
                
        merged["unique_customers"] += int(s.get("unique_customers") or 0)
        merged["unique_stores"] += int(s.get("unique_stores") or 0)

    if avg_count > 0:
        merged["average_amount"] = round(avg_sums / avg_count, 2)
    if merged["min_amount"] == float("inf"):
        merged["min_amount"] = 0.0
        
    if category_counts:
        merged["top_category"] = max(category_counts, key=category_counts.get)
        
    merged["monthly_trend"] = [
        {"month": month, "value": round(val, 2)}
        for month, val in sorted(monthly_map.items())
    ]
    
    merged["total_amount"] = round(merged["total_amount"], 2)
    
    return merged


def get_ai_answer(
    db           : Session,
    file_ids     : Union[int, List[int]],
    user_id      : int,
    user_question: str = None,
) -> dict:
    """
    Full RAG pipeline:
    1. Search Pinecone for relevant chunks
    2. Build prompt with retrieved context
    3. Call Ollama
    4. Save result to ai_insights table
    5. Return answer
    """
    if isinstance(file_ids, int):
        file_ids = [file_ids]

    primary_file_id = file_ids[0]

    # Load processed KPI summary for context
    processed_records = db.query(ProcessedDataset).filter(
        ProcessedDataset.file_id.in_(file_ids)
    ).all()

    if not processed_records:
        raise ValueError(
            "No processed data found. "
            "Run preprocessing and embedding first."
        )

    # Merge KPI summaries
    kpi_summaries = [p.kpi_summary for p in processed_records if p.kpi_summary]
    kpi_summary = merge_kpi_summaries(kpi_summaries)

    # ── Branch 1: Specific question — use RAG ──
    if user_question:
        # Search Pinecone for relevant chunks
        chunks = search_similar_chunks(
            query    = user_question,
            user_id  = user_id,
            file_ids = file_ids,
            top_k    = 5,
        )

        # Build RAG prompt
        prompt = build_rag_prompt(
            user_question    = user_question,
            retrieved_chunks = chunks,
            kpi_summary      = kpi_summary,
        )

    # ── Branch 2: No question — general analysis ──
    else:
        chunks = []
        prompt = build_general_insights_prompt(kpi_summary)

    # Call Ollama
    ai_response = call_ollama(prompt)

    # Save to ai_insights table under primary_file_id
    existing = db.query(AiInsight).filter(
        AiInsight.file_id == primary_file_id
    ).first()

    if existing:
        existing.prompt_used  = prompt
        existing.ai_response  = ai_response
        existing.model_name   = "llama 3.2"
    else:
        insight = AiInsight(
            file_id    = primary_file_id,
            model_name = "llama 3.2",
            prompt_used= prompt,
            ai_response= ai_response,
        )
        db.add(insight)

    db.commit()

    return {
        "file_ids"       : file_ids,
        "question"       : user_question or "General business analysis",
        "chunks_used"    : len(chunks),
        "ai_response"    : ai_response,
        "model"          : "llama 3.2",
    }