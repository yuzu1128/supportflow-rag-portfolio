from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterator


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SQLiteStore:
    db_path: Path

    def __post_init__(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init_db(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    source_path TEXT,
                    content_type TEXT NOT NULL,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    text TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS query_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    citations_json TEXT NOT NULL DEFAULT '[]',
                    abstained INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS evaluation_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    metrics_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL
                );
                """
            )

    def insert_document(
        self,
        *,
        doc_id: str,
        title: str,
        text: str,
        content_type: str,
        source_path: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        record = {
            "id": doc_id,
            "title": title,
            "source_path": source_path,
            "content_type": content_type,
            "metadata_json": json.dumps(metadata or {}, sort_keys=True),
            "text": text,
            "created_at": utc_now(),
        }
        with self.connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO documents
                    (id, title, source_path, content_type, metadata_json, text, created_at)
                VALUES
                    (:id, :title, :source_path, :content_type, :metadata_json, :text, :created_at)
                """,
                record,
            )
        return self._decode_document(record)

    def list_documents(self) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM documents ORDER BY created_at DESC, title ASC"
            ).fetchall()
        return [self._decode_document(dict(row)) for row in rows]

    def get_document(self, doc_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
        return self._decode_document(dict(row)) if row else None

    def add_query_log(
        self,
        *,
        question: str,
        answer: str,
        provider: str,
        citations: list[dict[str, Any]],
        abstained: bool,
    ) -> dict[str, Any]:
        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO query_logs
                    (question, answer, provider, citations_json, abstained, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    question,
                    answer,
                    provider,
                    json.dumps(citations, sort_keys=True),
                    int(abstained),
                    utc_now(),
                ),
            )
            log_id = cursor.lastrowid
        return self.get_query_log(int(log_id)) or {}

    def get_query_log(self, log_id: int) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM query_logs WHERE id = ?", (log_id,)).fetchone()
        return self._decode_query_log(dict(row)) if row else None

    def list_query_logs(self, limit: int = 50) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM query_logs ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [self._decode_query_log(dict(row)) for row in rows]

    def add_evaluation_run(self, *, name: str, metrics: dict[str, Any]) -> dict[str, Any]:
        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO evaluation_runs (name, metrics_json, created_at)
                VALUES (?, ?, ?)
                """,
                (name, json.dumps(metrics, sort_keys=True), utc_now()),
            )
            run_id = cursor.lastrowid
        return self.get_evaluation_run(int(run_id)) or {}

    def get_evaluation_run(self, run_id: int) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM evaluation_runs WHERE id = ?", (run_id,)
            ).fetchone()
        return self._decode_evaluation_run(dict(row)) if row else None

    def list_evaluation_runs(self, limit: int = 20) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM evaluation_runs ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [self._decode_evaluation_run(dict(row)) for row in rows]

    @staticmethod
    def _decode_document(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": row["id"],
            "title": row["title"],
            "source_path": row.get("source_path"),
            "content_type": row["content_type"],
            "metadata": json.loads(row.get("metadata_json") or "{}"),
            "text": row["text"],
            "created_at": row["created_at"],
        }

    @staticmethod
    def _decode_query_log(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": row["id"],
            "question": row["question"],
            "answer": row["answer"],
            "provider": row["provider"],
            "citations": json.loads(row.get("citations_json") or "[]"),
            "abstained": bool(row["abstained"]),
            "created_at": row["created_at"],
        }

    @staticmethod
    def _decode_evaluation_run(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": row["id"],
            "name": row["name"],
            "metrics": json.loads(row.get("metrics_json") or "{}"),
            "created_at": row["created_at"],
        }
