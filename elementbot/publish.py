"""Wysyłka do Telegrama. Token nigdy nie trafia do komunikatów błędów."""
from __future__ import annotations

import requests

API = "https://api.telegram.org/bot{token}/sendMessage"


class PublishError(Exception):
    pass


def send_message(token: str, chat_id: str, text: str) -> int | None:
    """Wysyła zwykły tekst (bez parse_mode). Zwraca message_id."""
    try:
        resp = requests.post(
            API.format(token=token),
            json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True},
            timeout=30,
        )
    except requests.RequestException as exc:
        # Celowo bez str(exc): komunikat może zawierać URL z tokenem.
        raise PublishError(f"Błąd sieci przy wysyłce do Telegrama ({type(exc).__name__})") from None

    try:
        payload = resp.json()
    except ValueError:
        payload = {}
    if resp.status_code != 200 or not payload.get("ok"):
        desc = str(payload.get("description", "brak opisu")).replace(token, "***")
        raise PublishError(f"Telegram odrzucił wiadomość: HTTP {resp.status_code}, {desc}")
    return payload.get("result", {}).get("message_id")
