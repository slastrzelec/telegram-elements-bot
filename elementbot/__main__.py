"""Punkt wejścia: python -m elementbot. Konfiguracja wyłącznie ze zmiennych środowiskowych."""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from .generate import generate_article
from .main import run
from .publish import PublishError, send_message

DEFAULT_MODEL = "claude-sonnet-5-5"
STATE_PATH = Path(__file__).resolve().parent.parent / "data" / "published.json"


def _env(name: str, required: bool = True) -> str:
    value = os.environ.get(name, "").strip()
    if required and not value:
        print(f"Brak wymaganej zmiennej środowiskowej: {name}", file=sys.stderr)
        sys.exit(2)
    return value


def main() -> int:
    dry_run = os.environ.get("DRY_RUN") == "1"
    force = os.environ.get("FORCE") == "1"

    api_key = _env("ANTHROPIC_API_KEY")
    token = _env("TELEGRAM_BOT_TOKEN", required=not dry_run)
    channel = _env("TELEGRAM_CHANNEL", required=not dry_run)
    owner = _env("OWNER_CHAT_ID", required=False)
    model = os.environ.get("ELEMENTBOT_MODEL", DEFAULT_MODEL)

    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    def make_article(el, issues):
        return generate_article(client, model, el, issues)

    def send(text):
        return send_message(token, channel, text)

    def notify(text):
        print(f"POWIADOMIENIE: {text}", file=sys.stderr)
        if owner and token:
            try:
                send_message(token, owner, text)
            except PublishError as exc:
                print(f"Nie udało się powiadomić właściciela: {exc}", file=sys.stderr)

    return run(
        now=datetime.now(timezone.utc),
        state_path=STATE_PATH,
        make_article=make_article,
        send=send,
        notify=notify,
        force=force,
        dry_run=dry_run,
    )


if __name__ == "__main__":
    sys.exit(main())
