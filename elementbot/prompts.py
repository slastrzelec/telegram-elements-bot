from __future__ import annotations

from .elements import Element

SYSTEM = """Jesteś autorem polskiego bloga popularnonaukowego i kanału na Telegramie. Piszesz artykuły o pierwiastkach chemicznych.

STYL (bezwzględnie):
- Język polski, jeden płynny tekst, ton ciekawy i przystępny.
- Pierwsza linia: tytuł z nazwą pierwiastka i emoji, potem krótki chwytliwy wstęp (hak).
- Treść: historia i odkrywca, budowa i właściwości, zastosowania, krótka sekcja zaczynająca się od "Ciekawostka na koniec:".
- ŻADNEJ składni Markdown: bez #, **, *, _, backticków, list, tabel, linków. Telegram tego nie renderuje. Akapity oddzielaj pustą linią.
- Gęste emoji: co najmniej jedno w każdym akapicie, plus kilka w tekście.
- Tekst krótki: około 1800-3000 znaków łącznie, nigdy więcej niż 3300.
- Ostatnia linia: wyłącznie 5-8 hashtagów oddzielonych spacją, np. #Miedz #Pierwiastki #Chemia. Wolno użyć nazwy pierwiastka i tematów szczegółowych. ZAKAZANE hashtagi: #edukacja #magnesy #przyroda #GFP #biofluorescencja #nauka.
- Nie dodawaj linku do kanału ani żadnych adresów URL.

RZETELNOŚĆ:
- Podawaj tylko fakty, których jesteś pewien. Daty, liczby i nazwiska zapisuj ostrożnie. Jeśli nie jesteś pewien, pomiń albo napisz "około" / "według większości źródeł".
- Nie wymyślaj anegdot ani cytatów.

BEZPIECZEŃSTWO:
- Dla pierwiastków i związków groźnych (toksycznych, promieniotwórczych, związanych z bronią) pisz wyłącznie o historii, mechanizmie działania i kontekście. Bez syntezy, pozyskiwania, proporcji, dawek, produkcji i instrukcji.
"""


def _element_line(el: Element) -> str:
    return f"{el.pl} (symbol {el.symbol}, liczba atomowa {el.z}, ang. {el.en})"


def _mode_note(el: Element) -> str:
    notes = []
    if el.careful:
        notes.append(
            "TRYB OSTROŻNY: ten pierwiastek jest słabo zbadany lub syntetyczny. Napisz krótszy tekst "
            "(około 1500-2200 znaków), unikaj konkretnych liczb poza tymi, których jesteś pewien, "
            "i jasno zaznacz, że dane są ograniczone."
        )
    if el.hazardous:
        notes.append(
            "TEMAT WRAŻLIWY: tylko historia, mechanizm i kontekst. Żadnych szczegółów produkcji ani pozyskiwania."
        )
    return "\n".join(notes)


def draft_prompt(el: Element, issues: list[str]) -> str:
    parts = [f"Napisz artykuł o pierwiastku: {_element_line(el)}."]
    note = _mode_note(el)
    if note:
        parts.append(note)
    if issues:
        parts.append(
            "Poprzednia próba została odrzucona z powodów:\n- " + "\n- ".join(issues) + "\nPopraw je."
        )
    parts.append("Zwróć wyłącznie gotowy tekst wewnątrz znaczników <artykul> i </artykul>, bez żadnego komentarza.")
    return "\n\n".join(parts)


def verify_prompt(el: Element, draft: str) -> str:
    note = _mode_note(el)
    return (
        f"Poniżej szkic artykułu o pierwiastku {_element_line(el)}.\n\n"
        "ZADANIE: zweryfikuj każde twierdzenie faktyczne (daty, liczby, nazwiska odkrywców, nazwy, zastosowania) "
        "za pomocą wyszukiwarki w sieci. Błędy popraw. Twierdzeń, których nie da się potwierdzić, usuń albo "
        "złagodz. Zachowaj styl, długość (nie dłużej niż 3300 znaków), brak Markdown, emoji w każdym akapicie, "
        "sekcję 'Ciekawostka na koniec' oraz ostatnią linię z hashtagami (bez zakazanych: #edukacja #magnesy "
        "#przyroda #GFP #biofluorescencja #nauka).\n"
        + (note + "\n" if note else "")
        + "\nSZKIC:\n<szkic>\n" + draft + "\n</szkic>\n\n"
        "Zwróć wyłącznie ostateczny, poprawiony tekst wewnątrz znaczników <artykul> i </artykul>. "
        "Żadnych komentarzy ani opisu zmian, ani przed, ani po znacznikach."
    )
