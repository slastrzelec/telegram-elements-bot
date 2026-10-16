"""Deterministyczna walidacja formatu artykułu (bez udziału modelu)."""
from __future__ import annotations

import re

MAX_LEN = 3500  # limit Telegrama to 4096, zostawiamy margines
MIN_LEN = 800
MIN_EMOJI = 8
FORBIDDEN_HASHTAGS = {
    "#edukacja", "#magnesy", "#przyroda", "#gfp", "#biofluorescencja", "#nauka",
}
REQUIRED_PHRASE = "Ciekawostka na koniec"

EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⭐⭕]")
HASHTAG = re.compile(r"#\w+", re.UNICODE)

MARKDOWN_PATTERNS = [
    (re.compile(r"\*\*"), "pogrubienie (**)"),
    (re.compile(r"__"), "podkreślenia (__)"),
    (re.compile(r"(?m)^\s{0,3}#{1,6}\s"), "nagłówek (#)"),
    (re.compile(r"`"), "backtick"),
    (re.compile(r"(?m)^\s*[-*+•]\s+\S"), "lista punktowana"),
    (re.compile(r"(?m)^\s*\d+[.)]\s+\S"), "lista numerowana"),
    (re.compile(r"(?m)^\s*\|.*\|"), "tabela"),
    (re.compile(r"\[[^\]]+\]\([^)]+\)"), "link Markdown"),
    (re.compile(r"(?<!\w)\*[^\s*][^*\n]*\*(?!\w)"), "kursywa (*)"),
]


def validate(text: str) -> list[str]:
    """Zwraca listę problemów. Pusta lista = tekst jest poprawny."""
    issues: list[str] = []
    text = text.strip()

    if len(text) > MAX_LEN:
        issues.append(f"Za długi: {len(text)} znaków (maks. {MAX_LEN})")
    if len(text) < MIN_LEN:
        issues.append(f"Za krótki: {len(text)} znaków (min. {MIN_LEN})")

    for pattern, label in MARKDOWN_PATTERNS:
        if pattern.search(text):
            issues.append(f"Składnia Markdown: {label}")

    if "t.me/" in text.lower():
        issues.append("Zawiera link do kanału (t.me)")

    for tag in HASHTAG.findall(text):
        if tag.lower() in FORBIDDEN_HASHTAGS:
            issues.append(f"Zakazany hashtag: {tag}")

    if REQUIRED_PHRASE not in text:
        issues.append(f"Brak sekcji '{REQUIRED_PHRASE}'")

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    last = lines[-1] if lines else ""
    tokens = last.split()
    if not tokens or not all(t.startswith("#") for t in tokens):
        issues.append("Ostatnia linia nie jest linią hashtagów")
    elif not 4 <= len(tokens) <= 10:
        issues.append(f"Liczba hashtagów w ostatniej linii: {len(tokens)} (powinno być 4-10)")

    # Treść bez ostatniej linii (hashtagi), z zachowaniem pustych linii między akapitami.
    body = text.rsplit(last, 1)[0] if last else text
    if len(EMOJI.findall(body)) < MIN_EMOJI:
        issues.append(f"Za mało emoji (min. {MIN_EMOJI})")
    for i, para in enumerate(re.split(r"\n\s*\n", body)):
        if para.strip() and not EMOJI.search(para):
            issues.append(f"Akapit {i + 1} bez emoji")

    return issues
