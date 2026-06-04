from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_store
from app.core.settings import get_settings
from app.db.sqlite import SQLiteStore
from app.llm.providers import safe_generate
from app.rag.search import ChromaReadyHybridIndex, build_documents
from app.schemas import AskRequest, AskResponse, Citation


router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest, store: SQLiteStore = Depends(get_store)) -> dict:
    settings = get_settings()
    documents = build_documents(store.list_documents())
    index = ChromaReadyHybridIndex(documents)
    results = index.search(request.question, k=request.k)
    filtered = [result for result in results if result.score >= request.abstain_threshold]
    abstained = not filtered
    context_limit = 1 if settings.llm_provider == "ollama" else 2
    generation_contexts = [] if abstained else filtered[:context_limit]
    response = safe_generate(settings, request.question, generation_contexts)
    citations = [
        Citation(
            document_id=result.document.id,
            title=result.document.title,
            score=result.score,
            snippet=result.snippet,
        )
        for result in filtered
    ]
    payload = {
        "question": request.question,
        "answer": response.answer,
        "provider": response.provider,
        "citations": citations,
        "abstained": abstained,
    }
    store.add_query_log(
        question=request.question,
        answer=response.answer,
        provider=response.provider,
        citations=[citation.model_dump() for citation in citations],
        abstained=abstained,
    )
    return payload
