from __future__ import annotations

from dataclasses import dataclass
from math import log, sqrt
import re
from typing import Protocol


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_]+")
DEFAULT_CHUNK_SIZE = 600
DEFAULT_CHUNK_OVERLAP = 120


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def identifier_tokens(tokens: list[str]) -> list[str]:
    return [token for token in tokens if "_" in token or any(char.isdigit() for char in token)]


@dataclass(frozen=True)
class SearchDocument:
    id: str
    title: str
    text: str
    metadata: dict


@dataclass(frozen=True)
class SearchChunk:
    id: str
    document: SearchDocument
    index: int
    text: str


@dataclass(frozen=True)
class SearchResult:
    document: SearchDocument
    score: float
    snippet: str
    chunk_id: str | None = None
    chunk_index: int | None = None


class SearchIndex(Protocol):
    def search(self, query: str, k: int = 4) -> list[SearchResult]:
        ...


class InMemoryHybridIndex:
    """Small deterministic BM25-like index used as the always-available fallback."""

    def __init__(self, documents: list[SearchDocument]) -> None:
        self.documents = documents
        self.chunks = [
            SearchChunk(
                id=f"{doc.id}#chunk-{index}",
                document=doc,
                index=index,
                text=chunk,
            )
            for doc in documents
            for index, chunk in enumerate(chunk_text(doc.text), start=1)
        ]
        self.chunk_tokens = {
            chunk.id: tokenize(f"{chunk.document.title} {chunk.text}") for chunk in self.chunks
        }
        self.document_frequency: dict[str, int] = {}
        for tokens in self.chunk_tokens.values():
            for token in set(tokens):
                self.document_frequency[token] = self.document_frequency.get(token, 0) + 1

    def search(self, query: str, k: int = 4) -> list[SearchResult]:
        query_tokens = tokenize(query)
        if not query_tokens:
            return []
        identifiers = identifier_tokens(query_tokens)

        best_by_document: dict[str, SearchResult] = {}
        total_chunks = max(len(self.chunks), 1)
        for chunk in self.chunks:
            tokens = self.chunk_tokens.get(chunk.id, [])
            if not tokens:
                continue
            term_counts: dict[str, int] = {}
            for token in tokens:
                term_counts[token] = term_counts.get(token, 0) + 1

            score = 0.0
            for token in query_tokens:
                if token not in term_counts:
                    continue
                idf = log((total_chunks + 1) / (self.document_frequency.get(token, 0) + 1)) + 1
                score += (1 + log(term_counts[token])) * idf
            if score <= 0:
                continue

            normalized = score / sqrt(len(tokens))
            matched_identifiers = sum(1 for token in identifiers if token in term_counts)
            if identifiers:
                if matched_identifiers:
                    normalized += matched_identifiers * 1.5
                else:
                    normalized *= 0.25
            result = SearchResult(
                document=chunk.document,
                score=normalized,
                snippet=make_snippet(chunk.text, query_tokens),
                chunk_id=chunk.id,
                chunk_index=chunk.index,
            )
            current = best_by_document.get(chunk.document.id)
            if current is None or result.score > current.score:
                best_by_document[chunk.document.id] = result

        scored = list(best_by_document.values())
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


def make_snippet(text: str, query_tokens: list[str], window: int = 360) -> str:
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


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    normalized = text.strip()
    if not normalized:
        return []

    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", normalized) if part.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(_split_long_text(paragraph, chunk_size, overlap))
            continue

        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)
        current = paragraph

    if current:
        chunks.append(current)
    return chunks or [normalized]


def chunk_count(text: str) -> int:
    return len(chunk_text(text))


def _split_long_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    chunks: list[str] = []
    step = max(chunk_size - overlap, 1)
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start += step
    return chunks


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
