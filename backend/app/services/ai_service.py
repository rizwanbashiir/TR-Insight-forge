from sqlalchemy.orm import Session

from app.models.ai_insight import AiInsight
from app.models.processed_dataset import ProcessedDataset
from app.models.uploaded_file import UploadedFile
from app.services.pinecone_service import search_similar_chunks
from app.services.prompt_builder import build_rag_prompt
from app.services.prompt_builder import build_general_insights_prompt
from app.services.ollama_service import call_ollama


def get_ai_answer(
    db           : Session,
    file_id      : int,
    user_id      : int,
    user_question: str = None,
) -> dict:
    """
    Full RAG pipeline:
    1. Search Pinecone for relevant chunks
    2. Build prompt with retrieved context
    3. Call Grok API
    4. Save result to ai_insights table
    5. Return answer
    """

    # Load processed KPI summary for context
    processed = db.query(ProcessedDataset).filter(
        ProcessedDataset.file_id == file_id
    ).first()

    file_record = db.query(UploadedFile).filter(
        UploadedFile.id == file_id
    ).first()

    if not processed:
        raise ValueError(
            "No processed data found. "
            "Run preprocessing and embedding first."
        )

    kpi_summary = processed.kpi_summary or {}

    # ── Branch 1: Specific question — use RAG ──
    if user_question:
        # Search Pinecone for relevant chunks
        chunks = search_similar_chunks(
            query   = user_question,
            user_id = user_id,
            file_id = file_id,
            top_k   = 5,
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

    # Save to ai_insights table
    existing = db.query(AiInsight).filter(
        AiInsight.file_id == file_id
    ).first()

    if existing:
        existing.prompt_used  = prompt
        existing.ai_response  = ai_response
        existing.model_name   = "llama-3.3-70b-versatile"
    else:
        insight = AiInsight(
            file_id    = file_id,
            model_name = "llama 3.2",
            prompt_used= prompt,
            ai_response= ai_response,
        )
        db.add(insight)

    db.commit()

    return {
        "file_id"        : file_id,
        "question"       : user_question or "General business analysis",
        "chunks_used"    : len(chunks),
        "ai_response"    : ai_response,
        "model"          : "llama 3.2",
    }