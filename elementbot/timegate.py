"""Bramka czasu: publikuj od 8:00 do 21:59 czasu warszawskiego, raz dziennie.

Harmonogram GitHub Actions bywa opóźniany o wiele godzin albo pomija
uruchomienia, więc workflow ma kilka wyzwalaczy w ciągu dnia (UTC), a bramka
zapewnia jedną publikację na dobę: pierwsze uruchomienie w oknie publikuje,
kolejne widzą wpis z dzisiejszą datą i kończą bez publikacji.
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from .state import published_dates

TZ = ZoneInfo("Europe/Warsaw")
START_HOUR = 8
END_HOUR = 22  # wyłącznie


def local_date(now: datetime) -> str:
    return now.astimezone(TZ).date().isoformat()


def should_publish_now(now: datetime, data: dict) -> bool:
    local = now.astimezone(TZ)
    if not (START_HOUR <= local.hour < END_HOUR):
        return False
    return local.date().isoformat() not in published_dates(data)
