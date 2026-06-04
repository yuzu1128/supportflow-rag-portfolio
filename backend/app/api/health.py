from fastapi import APIRouter, Depends

from app.api.deps import get_store
from app.core.settings import get_settings
from app.db.sqlite import SQLiteStore


router = APIRouter()


@router.get("/health")
def health(store: SQLiteStore = Depends(get_store)) -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "provider": settings.llm_provider,
        "document_count": len(store.list_documents()),
    }
