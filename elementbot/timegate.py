"""Bramka czasu: publikuj od 8:00 do 11:59 czasu warszawskiego, raz dziennie.

Cron działa w UTC, więc workflow uruchamia się o 06:00 i 07:00 UTC. Latem
pierwsze uruchomienie przypada na 8:00 lokalnie, zimą drugie. Drugie uruchomienie
latem widzi wpis z dzisiejszą datą i kończy bez publikacji.
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from .state import published_dates

TZ = ZoneInfo("Europe/Warsaw")
START_HOUR = 8
END_HOUR = 12  # wyłącznie


def local_date(now: datetime) -> str:
    return now.astimezone(TZ).date().isoformat()


def should_publish_now(now: datetime, data: dict) -> bool:
    local = now.astimezone(TZ)
    if not (START_HOUR <= local.hour < END_HOUR):
        return False
    return local.date().isoformat() not in published_dates(data)
