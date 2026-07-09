from beanie import PydanticObjectId
from typing import Union, List

from app.models.ai_insight import AIInsight
from app.models.processed_dataset import ProcessedDataset
from app.services.pinecone_service import search_similar_chunks
from app.services.prompt_builder import build_rag_prompt, build_general_insights_prompt
from app.services.grok_service import call_grok
from app.config.settings import settings


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


async def get_ai_answer(
    db,
    file_ids: Union[str, List[str]],
    user_id: str,
    user_question: str = None,
) -> dict:
    if isinstance(file_ids, (str, PydanticObjectId)):
        file_ids = [file_ids]

    primary_file_id = file_ids[0]
    primary_oid = PydanticObjectId(primary_file_id) if isinstance(primary_file_id, str) else primary_file_id
    oids = [PydanticObjectId(fid) if isinstance(fid, str) else fid for fid in file_ids]

    processed_records = await ProcessedDataset.find(
        {"file_id": {"$in": oids}}
    ).to_list()

    if not processed_records:
        raise ValueError(
            "No processed data found. "
            "Run preprocessing and embedding first."
        )

    kpi_summaries = [p.kpi_summary for p in processed_records if p.kpi_summary]
    kpi_summary = merge_kpi_summaries(kpi_summaries)

    if user_question:
        chunks = search_similar_chunks(
            query=user_question,
            user_id=user_id,
            file_ids=file_ids,
            top_k=5,
        )

        prompt = build_rag_prompt(
            user_question=user_question,
            retrieved_chunks=chunks,
            kpi_summary=kpi_summary,
        )
    else:
        chunks = []
        prompt = build_general_insights_prompt(kpi_summary)

    ai_response = call_grok(prompt)

    existing = await AIInsight.find_one(
        AIInsight.file_id == primary_oid
    )

    if existing:
        existing.prompt_used = prompt
        existing.ai_response = ai_response
        existing.model_name = settings.GROK_MODEL
        await existing.save()
    else:
        insight = AIInsight(
            file_id=primary_oid,
            model_name=settings.GROK_MODEL,
            prompt_used=prompt,
            ai_response=ai_response,
        )
        await insight.insert()

    return {
        "file_ids": file_ids,
        "question": user_question or "General business analysis",
        "chunks_used": len(chunks),
        "ai_response": ai_response,
        "model": settings.GROK_MODEL,
    }