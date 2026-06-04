from __future__ import annotations

from dataclasses import dataclass
import re
import httpx

from app.core.settings import Settings
from app.rag.search import SearchResult


class ProviderUnavailable(RuntimeError):
    pass


ANSWER_INSTRUCTION = (
    "Use only the retrieved context. "
    "Answer strictly in Japanese. "
    "Keep the answer concise and operational. "
    "Always cite sources with labels like [source: document_id]. "
    "If a recommended action is present, state that action first. "
    "In API error contexts, translate key rotation as API key rotation, "
    "not as rotating a person or administrator. "
    "Use this terminology: customer admin = kokyaku kanrisha; "
    "rotate or verify the key = API key rotation or verification; "
    "Ask the customer admin to rotate or verify the key = "
    "kokyaku kanrisha ni API key no rotation matawa kakunin wo irai suru. "
    "Do not invent source names or cite sources that are not shown below. "
    "For citations, use only the document_id shown in each Source header; "
    "ignore source_id fields inside CSV or JSON data. "
    "If the context is insufficient, say in Japanese that there is not enough "
    "grounded information to answer."
)


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
                "登録済み文書だけでは、この質問に回答するための十分な根拠が見つかりませんでした。",
                self.name,
            )

        top = contexts[0]
        sentence = _first_sentence(top.document.text) or top.snippet
        return LLMResponse(
            f"登録済み文書では、該当箇所に「{sentence}」と記載されています。 [source: {top.document.id}]",
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
                    {
                        "role": "system",
                        "content": ANSWER_INSTRUCTION,
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        return LLMResponse(normalize_answer(answer), self.name)


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
                "options": {
                    "temperature": 0,
                    "num_ctx": 512,
                    "num_predict": 180,
                },
            },
            timeout=120,
        )
        response.raise_for_status()
        answer = response.json().get("response", "").strip()
        if not answer:
            raise ProviderUnavailable("Ollama returned an empty response.")
        return LLMResponse(normalize_answer(answer), self.name)


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
        f"Source {idx + 1} document_id={result.document.id} title={result.document.title}:\n"
        f"{result.snippet}"
        for idx, result in enumerate(contexts)
    )
    if not context_text:
        context_text = "No retrieved context."
    return (
        f"{ANSWER_INSTRUCTION}\n\n"
        "Question:\n"
        f"{question}\n\n"
        "Retrieved context:\n"
        f"{context_text}\n\n"
        "Answer in Japanese with citations:"
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
            "available_without_network": True,
        },
    ]


def normalize_answer(answer: str) -> str:
    replacements = {
        "Auth_401": "AUTH_401",
        "auth_401": "AUTH_401",
        "お客様Admin": "顧客管理者",
        "お客様ADMIN": "顧客管理者",
        "お客様 admin": "顧客管理者",
        "adminを回転させたり、検証させる": "顧客管理者にAPIキーのローテーションまたは確認を依頼する",
        "キーを回転させたり、再確認してもらってください": "APIキーのローテーションまたは確認を依頼してください",
        "キーを回転させるか検証": "APIキーをローテーションまたは確認",
    }
    normalized = answer
    for before, after in replacements.items():
        normalized = normalized.replace(before, after)
    return re.sub(r"\[source:\s*([^,\]\s]+)[^\]]*\]", r"[source: \1]", normalized)


def _first_sentence(text: str) -> str:
    normalized = " ".join(text.split())
    for delimiter in [". ", "? ", "! ", "\n"]:
        if delimiter in normalized:
            return normalized.split(delimiter, 1)[0].strip() + delimiter.strip()
    return normalized[:280]
