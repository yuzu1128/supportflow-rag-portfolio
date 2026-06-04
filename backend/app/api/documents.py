from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_store
from app.core.settings import get_settings
from app.db.sqlite import SQLiteStore
from app.documents.loaders import DocumentLoadError, load_document
from app.rag.search import ChromaReadyHybridIndex, build_documents
from app.schemas import (
    Citation,
    DocumentListResponse,
    DocumentRegisterRequest,
    DocumentResponse,
    SearchRequest,
    SearchResponse,
)


router = APIRouter()
SUPPORTED_SAMPLE_SUFFIXES = {".md", ".markdown", ".txt", ".json", ".csv", ".pdf", ".docx"}


def _sample_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in SUPPORTED_SAMPLE_SUFFIXES:
            files.append(path)
    return sorted(files)


def _sample_metadata(path: Path, root: Path) -> dict:
    relative = path.relative_to(root)
    category = relative.parts[0] if len(relative.parts) > 1 else "uncategorized"
    virtual_type = path.suffix.lower().lstrip(".")
    if path.name.endswith(".pdf.txt"):
        virtual_type = "pdf"
    if path.name.endswith(".docx.txt"):
        virtual_type = "docx"
    return {
        "filename": path.name,
        "category": category,
        "relative_path": str(relative).replace("\\", "/"),
        "document_type": virtual_type,
        "owner": "Northstar Systems",
        "environment": "Local Demo",
    }


def index_sample_documents(store: SQLiteStore) -> list[dict]:
    settings = get_settings()
    root = settings.sample_docs_dir
    indexed: list[dict] = []
    for path in _sample_files(root):
        try:
            loaded = load_document(path)
        except DocumentLoadError:
            continue
        metadata = {**loaded.metadata, **_sample_metadata(path, root)}
        doc_id = metadata["relative_path"]
        indexed.append(
            store.insert_document(
                doc_id=doc_id,
                title=loaded.title.replace("_", " ").title(),
                text=loaded.text,
                content_type=loaded.content_type,
                source_path=str(path),
                metadata=metadata,
            )
        )
    return indexed


@router.post("", response_model=DocumentResponse)
def register_document(
    request: DocumentRegisterRequest, store: SQLiteStore = Depends(get_store)
) -> dict:
    if request.source_path:
        try:
            loaded = load_document(request.source_path)
        except DocumentLoadError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        title = request.title or loaded.title
        text = loaded.text
        content_type = request.content_type or loaded.content_type
        metadata = {**loaded.metadata, **request.metadata}
        source_path = str(Path(request.source_path).expanduser())
    else:
        if not request.text:
            raise HTTPException(status_code=400, detail="Provide either text or source_path.")
        title = request.title or "Untitled document"
        text = request.text
        content_type = request.content_type or "text/plain"
        metadata = request.metadata
        source_path = None

    return store.insert_document(
        doc_id=str(uuid4()),
        title=title,
        text=text,
        content_type=content_type,
        source_path=source_path,
        metadata=metadata,
    )


@router.get("", response_model=DocumentListResponse)
def list_documents(store: SQLiteStore = Depends(get_store)) -> dict:
    return {"documents": store.list_documents()}


@router.post("/index-sample", response_model=DocumentListResponse)
def index_sample(store: SQLiteStore = Depends(get_store)) -> dict:
    documents = index_sample_documents(store)
    return {"documents": documents}


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, store: SQLiteStore = Depends(get_store)) -> dict:
    document = store.get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return document


@router.post("/search", response_model=SearchResponse)
def search_documents(
    request: SearchRequest, store: SQLiteStore = Depends(get_store)
) -> dict:
    documents = build_documents(store.list_documents())
    index = ChromaReadyHybridIndex(documents)
    results = index.search(request.query, k=request.k)
    return {
        "query": request.query,
        "results": [
            Citation(
                document_id=result.document.id,
                title=result.document.title,
                score=result.score,
                snippet=result.snippet,
            )
            for result in results
        ],
    }
