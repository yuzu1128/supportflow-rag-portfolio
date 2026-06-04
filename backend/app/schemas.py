from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class DocumentRegisterRequest(BaseModel):
    title: str | None = None
    text: str | None = None
    source_path: str | None = None
    content_type: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentResponse(BaseModel):
    id: str
    title: str
    source_path: str | None = None
    content_type: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    text: str
    created_at: str


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]


class SearchRequest(BaseModel):
    query: str
    k: int = Field(default=4, ge=1, le=20)


class Citation(BaseModel):
    document_id: str
    title: str
    score: float
    snippet: str
    chunk_id: str | None = None
    chunk_index: int | None = None


class SearchResponse(BaseModel):
    query: str
    results: list[Citation]


class AskRequest(BaseModel):
    question: str
    k: int = Field(default=4, ge=1, le=20)
    abstain_threshold: float = Field(default=0.001, ge=0)


class AskResponse(BaseModel):
    question: str
    answer: str
    provider: str
    citations: list[Citation]
    abstained: bool


class EvaluationRunRequest(BaseModel):
    name: str = "local-evaluation"
    k: int = Field(default=4, ge=1, le=20)


class EvaluationRunResponse(BaseModel):
    id: int | None = None
    name: str
    available: bool
    dataset_path: str | None = None
    case_count: int
    metrics: dict[str, float]
    message: str | None = None


class LogListResponse(BaseModel):
    logs: list[dict[str, Any]]


class ProvidersResponse(BaseModel):
    active_provider: str
    providers: list[dict[str, Any]]
