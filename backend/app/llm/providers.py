from __future__ import annotations

from dataclasses import dataclass
import httpx

from app.core.settings import Settings
from app.rag.search import SearchResult


class ProviderUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class LLMResponse:
    answer: str
    provider: str


class BaseProvider:
    name = "base"

    def generate(self, question: str, contexts: list[SearchResult]) -> LLMResponse:
        raise NotImplementedError


class MockProvider(BaseProvider):
    name = "mock"

    def generate(self, question: str, contexts: list[SearchResult]) -> LLMResponse:
        if not contexts:
            return LLMResponse(
                "I do not have enough information in the registered documents to answer.",
                self.name,
            )

        top = contexts[0]
        sentence = _first_sentence(top.document.text) or top.snippet
        return LLMResponse(
            f"{sentence} [source: {top.document.id}]",
            self.name,
        )


class OpenRouterProvider(BaseProvider):
    name = "openrouter"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate(self, question: str, contexts: list[SearchResult]) -> LLMResponse:
        if not self.settings.openrouter_api_key:
            raise ProviderUnavailable("OPENROUTER_API_KEY is not configured.")
        if not self.settings.openrouter_model:
            raise ProviderUnavailable("OPENROUTER_MODEL is not configured.")

        prompt = build_prompt(question, contexts)
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.settings.openrouter_model,
                "messages": [
                    {"role": "system", "content": "Answer using only the provided context. Cite sources."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        return LLMResponse(answer, self.name)


class OllamaProvider(BaseProvider):
    name = "ollama"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate(self, question: str, contexts: list[SearchResult]) -> LLMResponse:
        if not self.settings.ollama_model:
            raise ProviderUnavailable("OLLAMA_MODEL is not configured.")
        prompt = build_prompt(question, contexts)
        response = httpx.post(
            f"{self.settings.ollama_base_url}/api/generate",
            json={
                "model": self.settings.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0},
            },
            timeout=30,
        )
        response.raise_for_status()
        answer = response.json().get("response", "").strip()
        if not answer:
            raise ProviderUnavailable("Ollama returned an empty response.")
        return LLMResponse(answer, self.name)


def get_provider(settings: Settings) -> BaseProvider:
    if settings.llm_provider == "openrouter":
        return OpenRouterProvider(settings)
    if settings.llm_provider == "ollama":
        return OllamaProvider(settings)
    return MockProvider()


def safe_generate(settings: Settings, question: str, contexts: list[SearchResult]) -> LLMResponse:
    provider = get_provider(settings)
    try:
        return provider.generate(question, contexts)
    except Exception:
        return MockProvider().generate(question, contexts)


def build_prompt(question: str, contexts: list[SearchResult]) -> str:
    context_text = "\n\n".join(
        f"Source {idx + 1} ({result.document.id}, {result.document.title}):\n{result.snippet}"
        for idx, result in enumerate(contexts)
    )
    if not context_text:
        context_text = "No retrieved context."
    return (
        "Question:\n"
        f"{question}\n\n"
        "Context:\n"
        f"{context_text}\n\n"
        "If the context is insufficient, say you do not have enough information."
    )


def provider_status(settings: Settings) -> list[dict[str, object]]:
    return [
        {
            "name": "mock",
            "configured": True,
            "available_without_network": True,
        },
        {
            "name": "openrouter",
            "configured": bool(settings.openrouter_api_key and settings.openrouter_model),
            "model": settings.openrouter_model or "selected later",
            "available_without_network": False,
        },
        {
            "name": "ollama",
            "configured": bool(settings.ollama_base_url and settings.ollama_model),
            "base_url": settings.ollama_base_url,
            "model": settings.ollama_model or "local model selected later",
            "available_without_network": False,
        },
    ]


def _first_sentence(text: str) -> str:
    normalized = " ".join(text.split())
    for delimiter in [". ", "? ", "! ", "\n"]:
        if delimiter in normalized:
            return normalized.split(delimiter, 1)[0].strip() + delimiter.strip()
    return normalized[:280]
