"""Generowanie artykułu: szkic, potem weryfikacja z wyszukiwarką.

Dwa wymienne backendy:
- ApiBackend: bezpośrednie wywołania API (klucz ANTHROPIC_API_KEY, rozliczenie API),
- CliBackend: Claude Code w trybie bez interfejsu (token CLAUDE_CODE_OAUTH_TOKEN,
  zużywa limit subskrypcji).
"""
from __future__ import annotations

import os
import re
import subprocess
import tempfile

from .elements import Element
from .prompts import SYSTEM, draft_prompt, verify_prompt

ARTICLE_RE = re.compile(r"<artykul>(.*?)</artykul>", re.S)
WEB_SEARCH_TOOL = {"type": "web_search_20250305", "name": "web_search", "max_uses": 6}
MAX_PAUSES = 4
CLI_TIMEOUT_S = 600
# Zmienne, które przestawiłyby CLI na rozliczenie API zamiast subskrypcji.
CLI_STRIPPED_ENV = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")
CLI_DENIED_TOOLS = "Bash,Edit,Write,Read,NotebookEdit,WebFetch"


class GenerationError(Exception):
    pass


class ApiBackend:
    def __init__(self, client, model: str):
        self.client = client
        self.model = model

    def complete(self, prompt: str, *, search: bool, max_tokens: int) -> str:
        kwargs = {
            "model": self.model, "system": SYSTEM, "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if search:
            kwargs["tools"] = [WEB_SEARCH_TOOL]
        texts: list[str] = []
        for _ in range(MAX_PAUSES):
            resp = self.client.messages.create(**kwargs)
            texts.extend(b.text for b in resp.content if getattr(b, "type", None) == "text")
            if getattr(resp, "stop_reason", None) != "pause_turn":
                return "".join(texts)
            kwargs["messages"] = kwargs["messages"] + [{"role": "assistant", "content": resp.content}]
        raise GenerationError("Model zbyt długo wstrzymywał turę (pause_turn)")


class CliBackend:
    """Claude Code (`claude -p`) uwierzytelniony tokenem subskrypcji."""

    def __init__(self, model: str | None = None, runner=subprocess.run, timeout: int = CLI_TIMEOUT_S):
        self.model = model
        self.runner = runner
        self.timeout = timeout

    def _command(self, prompt: str, search: bool) -> list[str]:
        denied = CLI_DENIED_TOOLS if search else CLI_DENIED_TOOLS + ",WebSearch"
        cmd = [
            "claude", "-p", prompt,
            "--output-format", "text",
            "--append-system-prompt", SYSTEM,
            "--max-turns", "10" if search else "2",
            "--disallowedTools", denied,
        ]
        if search:
            cmd += ["--allowedTools", "WebSearch"]
        if self.model:
            cmd += ["--model", self.model]
        return cmd

    def complete(self, prompt: str, *, search: bool, max_tokens: int | None = None) -> str:
        env = {k: v for k, v in os.environ.items() if k not in CLI_STRIPPED_ENV}
        token = env.get("CLAUDE_CODE_OAUTH_TOKEN", "")
        with tempfile.TemporaryDirectory() as workdir:  # pusty katalog: brak kontekstu projektu
            try:
                proc = self.runner(
                    self._command(prompt, search), capture_output=True, text=True,
                    encoding="utf-8", timeout=self.timeout, env=env, cwd=workdir,
                )
            except subprocess.TimeoutExpired:
                raise GenerationError("Przekroczono limit czasu polecenia claude") from None
            except FileNotFoundError:
                raise GenerationError("Nie znaleziono polecenia 'claude' (Claude Code CLI)") from None
        if proc.returncode != 0:
            detail = ((proc.stderr or "").strip() or (proc.stdout or "").strip())[-300:]
            if token:
                detail = detail.replace(token, "***")
            raise GenerationError(f"Polecenie claude zakończyło się kodem {proc.returncode}: {detail}")
        return proc.stdout


def extract_article(raw: str) -> str:
    matches = ARTICLE_RE.findall(raw)
    if not matches:
        raise GenerationError("Odpowiedź modelu bez znaczników <artykul>")
    text = matches[-1].strip()
    if not text:
        raise GenerationError("Pusty artykuł w odpowiedzi modelu")
    return text


def generate_article(backend, el: Element, issues: list[str] | None = None) -> str:
    draft = extract_article(
        backend.complete(draft_prompt(el, issues or []), search=False, max_tokens=3000)
    )
    return extract_article(
        backend.complete(verify_prompt(el, draft), search=True, max_tokens=4000)
    )
