from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ask, dashboard, documents, evaluation, health, logs
from app.api.deps import get_store
from app.api.documents import index_sample_documents


@asynccontextmanager
async def lifespan(app: FastAPI):
    store = get_store()
    if not store.list_documents():
        index_sample_documents(store)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="SupportFlow RAG Portfolio API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api", tags=["health"])
    app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
    app.include_router(ask.router, prefix="/api", tags=["ask"])
    app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
    app.include_router(evaluation.router, prefix="/api/evaluation", tags=["evaluation"])
    app.include_router(logs.router, prefix="/api/logs", tags=["logs"])

    @app.get("/health", tags=["health"])
    def root_health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
