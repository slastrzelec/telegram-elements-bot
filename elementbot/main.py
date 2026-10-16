"""Logika główna. Zależności wstrzykiwane, dzięki czemu da się to przetestować."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Callable

from . import state as st
from .generate import GenerationError
from .publish import PublishError
from .queue import next_element
from .timegate import local_date, should_publish_now
from .validate import validate

MAX_ATTEMPTS = 3


def run(
    *,
    now: datetime,
    state_path: Path,
    make_article: Callable,  # (element, issues) -> str
    send: Callable[[str], int | None],
    notify: Callable[[str], None],
    force: bool = False,
    dry_run: bool = False,
    log: Callable[[str], None] = print,
) -> int:
    data = st.load(state_path)

    if not force and not should_publish_now(now, data):
        log("Poza oknem publikacji lub dziś już opublikowano. Koniec.")
        return 0

    el = next_element(data)
    if el is None:
        notify("Kolejka pierwiastków jest pusta: opublikowano wszystkie 118. Potrzebna nowa seria.")
        log("Kolejka pusta.")
        return 0

    log(f"Następny pierwiastek: {el.pl} ({el.symbol}, Z={el.z})")

    issues: list[str] = []
    text: str | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            candidate = make_article(el, issues)
        except GenerationError as exc:
            issues = [str(exc)]
            log(f"Próba {attempt}: błąd generowania: {exc}")
            continue
        issues = validate(candidate)
        if not issues:
            text = candidate.strip()
            break
        log(f"Próba {attempt}: walidacja nieudana: {'; '.join(issues)}")

    if text is None:
        notify(
            f"Bot nie opublikował artykułu o pierwiastku {el.pl} ({el.symbol}) po {MAX_ATTEMPTS} próbach.\n"
            "Ostatnie problemy: " + "; ".join(issues)
        )
        return 1

    if dry_run:
        log("DRY_RUN: poniżej wygenerowany artykuł, bez publikacji i bez zapisu stanu.\n")
        log(text)
        return 0

    try:
        message_id = send(text)
    except PublishError as exc:
        notify(f"Publikacja pierwiastka {el.pl} nie powiodła się: {exc}")
        log(f"Błąd publikacji: {exc}")
        return 1

    st.mark_published(data, el.z, el.symbol, local_date(now), message_id)
    st.save(state_path, data)
    log(f"Opublikowano: {el.pl} (message_id={message_id}).")
    return 0
