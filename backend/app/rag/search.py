from __future__ import annotations

from dataclasses import dataclass
from math import log, sqrt
import re
from typing import Protocol


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


@dataclass(frozen=True)
class SearchDocument:
    id: str
    title: str
    text: str
    metadata: dict


@dataclass(frozen=True)
class SearchResult:
    document: SearchDocument
    score: float
    snippet: str


class SearchIndex(Protocol):
    def search(self, query: str, k: int = 4) -> list[SearchResult]:
        ...


class InMemoryHybridIndex:
    """Small deterministic BM25-like index used as the always-available fallback."""

    def __init__(self, documents: list[SearchDocument]) -> None:
        self.documents = documents
        self.doc_tokens = {doc.id: tokenize(f"{doc.title} {doc.text}") for doc in documents}
        self.document_frequency: dict[str, int] = {}
        for tokens in self.doc_tokens.values():
            for token in set(tokens):
                self.document_frequency[token] = self.document_frequency.get(token, 0) + 1

    def search(self, query: str, k: int = 4) -> list[SearchResult]:
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scored: list[SearchResult] = []
        total_docs = max(len(self.documents), 1)
        for doc in self.documents:
            tokens = self.doc_tokens.get(doc.id, [])
            if not tokens:
                continue
            term_counts: dict[str, int] = {}
            for token in tokens:
                term_counts[token] = term_counts.get(token, 0) + 1

            score = 0.0
            for token in query_tokens:
                if token not in term_counts:
                    continue
                idf = log((total_docs + 1) / (self.document_frequency.get(token, 0) + 1)) + 1
                score += (1 + log(term_counts[token])) * idf
            if score <= 0:
                continue

            normalized = score / sqrt(len(tokens))
            scored.append(SearchResult(doc, normalized, make_snippet(doc.text, query_tokens)))

        scored.sort(key=lambda item: (-item.score, item.document.title, item.document.id))
        return scored[: max(k, 0)]


class ChromaReadyHybridIndex:
    """Chroma-compatible shell with deterministic local fallback.

    The class is intentionally light: if chromadb is installed later, callers can pass
    use_chroma=True and build out persistence without changing route code. Until then,
    search remains local and testable.
    """

    def __init__(self, documents: list[SearchDocument], use_chroma: bool = False) -> None:
        self.fallback = InMemoryHybridIndex(documents)
        self.chroma_available = False
        if use_chroma:
            try:
                import chromadb  # noqa: F401

                self.chroma_available = True
            except ImportError:
                self.chroma_available = False

    def search(self, query: str, k: int = 4) -> list[SearchResult]:
        return self.fallback.search(query, k)


def make_snippet(text: str, query_tokens: list[str], window: int = 180) -> str:
    lower_text = text.lower()
    first_hit = min(
        (lower_text.find(token) for token in query_tokens if lower_text.find(token) >= 0),
        default=0,
    )
    start = max(first_hit - window // 3, 0)
    end = min(start + window, len(text))
    snippet = text[start:end].strip()
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet += "..."
    return snippet


def build_documents(records: list[dict]) -> list[SearchDocument]:
    return [
        SearchDocument(
            id=record["id"],
            title=record["title"],
            text=record["text"],
            metadata=record.get("metadata") or {},
        )
        for record in records
    ]
