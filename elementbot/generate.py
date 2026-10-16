"""Generowanie artykułu: szkic, potem weryfikacja z wyszukiwarką."""
from __future__ import annotations

import re

from .elements import Element
from .prompts import SYSTEM, draft_prompt, verify_prompt

ARTICLE_RE = re.compile(r"<artykul>(.*?)</artykul>", re.S)
WEB_SEARCH_TOOL = {"type": "web_search_20250305", "name": "web_search", "max_uses": 6}
MAX_PAUSES = 4


class GenerationError(Exception):
    pass


def _call(client, *, model: str, messages: list, max_tokens: int, tools: list | None = None) -> str:
    """Wywołuje API; obsługuje pause_turn przy narzędziach serwerowych. Zwraca cały tekst."""
    kwargs = {"model": model, "system": SYSTEM, "messages": list(messages), "max_tokens": max_tokens}
    if tools:
        kwargs["tools"] = tools
    texts: list[str] = []
    for _ in range(MAX_PAUSES):
        resp = client.messages.create(**kwargs)
        texts.extend(b.text for b in resp.content if getattr(b, "type", None) == "text")
        if getattr(resp, "stop_reason", None) != "pause_turn":
            return "".join(texts)
        kwargs["messages"] = kwargs["messages"] + [{"role": "assistant", "content": resp.content}]
    raise GenerationError("Model zbyt długo wstrzymywał turę (pause_turn)")


def extract_article(raw: str) -> str:
    matches = ARTICLE_RE.findall(raw)
    if not matches:
        raise GenerationError("Odpowiedź modelu bez znaczników <artykul>")
    text = matches[-1].strip()
    if not text:
        raise GenerationError("Pusty artykuł w odpowiedzi modelu")
    return text


def generate_article(client, model: str, el: Element, issues: list[str] | None = None) -> str:
    draft_raw = _call(
        client, model=model, max_tokens=3000,
        messages=[{"role": "user", "content": draft_prompt(el, issues or [])}],
    )
    draft = extract_article(draft_raw)

    final_raw = _call(
        client, model=model, max_tokens=4000, tools=[WEB_SEARCH_TOOL],
        messages=[{"role": "user", "content": verify_prompt(el, draft)}],
    )
    return extract_article(final_raw)
