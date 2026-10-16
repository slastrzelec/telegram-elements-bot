import pytest

from elementbot.validate import validate


def test_good_article_passes(good_article):
    assert validate(good_article) == []


@pytest.mark.parametrize(
    "mutate, expected",
    [
        (lambda t: t.replace("Żelazo:", "**Żelazo**:", 1), "pogrubienie"),
        (lambda t: "## Nagłówek\n\n" + t, "nagłówek"),
        (lambda t: t.replace("📜 Ludzie", "- Ludzie", 1), "lista punktowana"),
        (lambda t: t.replace("#Chemia", "#nauka"), "Zakazany hashtag"),
        (lambda t: t.replace("#Chemia", "#Edukacja"), "Zakazany hashtag"),
        (lambda t: t + " https://t.me/naukowy_tg", "t.me"),
        (lambda t: t.replace("Ciekawostka na koniec", "Na koniec"), "Ciekawostka na koniec"),
        (lambda t: t.rsplit("\n\n", 1)[0], "hashtag"),
        (lambda t: t + "\n\n" + "x" * 3000, "Za długi"),
        (lambda t: "krótki tekst 🙂\n\n#A #B #C #D", "Za krótki"),
    ],
)
def test_bad_variants_are_rejected(good_article, mutate, expected):
    issues = validate(mutate(good_article))
    assert any(expected.lower() in i.lower() for i in issues), issues


def test_paragraph_without_emoji_is_rejected(good_article):
    broken = good_article.replace(
        "🏭 Dziś żelazo i stal to fundament budownictwa, motoryzacji, maszyn i infrastruktury, a rocznie produkuje się ich ponad miliard ton. 🚗 To nasz najważniejszy metal techniczny i prawdopodobnie jeszcze długo nim pozostanie. 🌉",
        "Dziś żelazo i stal to fundament budownictwa, motoryzacji, maszyn i infrastruktury.",
    )
    assert any("bez emoji" in i for i in validate(broken))


def test_morse_style_dashes_are_not_flagged_as_markdown(good_article):
    text = good_article.replace("Gdy bierzesz", "Sygnał ···---··· znamy wszyscy. Gdy bierzesz", 1)
    assert validate(text) == []
