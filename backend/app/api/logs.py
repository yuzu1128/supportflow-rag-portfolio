from fastapi import APIRouter, Depends, Query

from app.api.deps import get_store
from app.core.settings import get_settings
from app.db.sqlite import SQLiteStore
from app.llm.providers import provider_status
from app.schemas import LogListResponse, ProvidersResponse


router = APIRouter()


@router.get("", response_model=LogListResponse)
def logs(
    limit: int = Query(default=50, ge=1, le=200),
    store: SQLiteStore = Depends(get_store),
) -> dict:
    return {"logs": store.list_query_logs(limit=limit)}


@router.get("/providers", response_model=ProvidersResponse)
def providers() -> dict:
    settings = get_settings()
    return {
        "active_provider": settings.llm_provider,
        "providers": provider_status(settings),
    }
