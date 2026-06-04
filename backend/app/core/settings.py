from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    llm_provider: str = "mock"
    openrouter_api_key: str = ""
    openrouter_model: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = ""
    data_dir: Path = Path("data")
    sample_docs_dir: Path = Path("sample_docs")

    @property
    def database_path(self) -> Path:
        return self.data_dir / "supportflow.sqlite3"


def get_settings() -> Settings:
    data_dir = Path(os.getenv("DATA_DIR", "data")).expanduser()
    sample_docs_dir = Path(os.getenv("SAMPLE_DOCS_DIR", "sample_docs")).expanduser()
    return Settings(
        llm_provider=os.getenv("LLM_PROVIDER", "mock").strip().lower() or "mock",
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        openrouter_model=os.getenv("OPENROUTER_MODEL", ""),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/"),
        ollama_model=os.getenv("OLLAMA_MODEL", ""),
        data_dir=data_dir,
        sample_docs_dir=sample_docs_dir,
    )
