from types import SimpleNamespace

import pytest
import requests

from elementbot import state as st
from elementbot.generate import GenerationError, extract_article, generate_article
from elementbot.main import run
from elementbot.publish import PublishError, send_message
from elementbot.elements import ELEMENTS

from conftest import utc

NOW = utc(2026, 7, 1, 6, 10)  # 8:10 w Warszawie


class Recorder:
    def __init__(self):
        self.sent, self.notes = [], []

    def send(self, text):
        self.sent.append(text)
        return 777

    def notify(self, text):
        self.notes.append(text)


def go(state_file, make_article, rec, **kw):
    return run(
        now=kw.pop("now", NOW), state_path=state_file, make_article=make_article,
        send=kw.pop("send", rec.send), notify=rec.notify, log=lambda *_: None, **kw,
    )


def test_happy_path_publishes_once_and_marks_state(state_file, good_article):
    rec = Recorder()
    assert go(state_file, lambda el, issues: good_article, rec) == 0
    assert rec.sent == [good_article] and rec.notes == []
    data = st.load(state_file)
    assert data["published"][-1]["symbol"] == "H"
    assert data["published"][-1]["date"] == "2026-07-01"
    assert data["published"][-1]["message_id"] == 777
    # drugie uruchomienie tego samego dnia (drugi cron) nic nie robi
    assert go(state_file, lambda el, issues: good_article, rec, now=utc(2026, 7, 1, 7, 10)) == 0
    assert len(rec.sent) == 1


def test_outside_window_does_nothing(state_file, good_article):
    rec = Recorder()
    assert go(state_file, lambda el, issues: good_article, rec, now=utc(2026, 7, 1, 2, 0)) == 0
    assert rec.sent == []


def test_invalid_article_three_attempts_then_notify_and_no_state_change(state_file):
    rec = Recorder()
    calls = []

    def bad(el, issues):
        calls.append(list(issues))
        return "**źle**"

    before = st.load(state_file)
    assert go(state_file, bad, rec) == 1
    assert len(calls) == 3
    assert calls[0] == [] and calls[1] != []  # uwagi wracają do modelu
    assert rec.sent == [] and len(rec.notes) == 1
    assert st.load(state_file) == before


def test_retry_succeeds_on_second_attempt(state_file, good_article):
    rec = Recorder()
    seq = iter(["**źle**", good_article])
    assert go(state_file, lambda el, issues: next(seq), rec) == 0
    assert len(rec.sent) == 1


def test_generation_error_is_retried_and_reported(state_file):
    rec = Recorder()

    def boom(el, issues):
        raise GenerationError("brak znaczników")

    assert go(state_file, boom, rec) == 1
    assert "brak znaczników" in rec.notes[0]


def test_publish_failure_notifies_and_does_not_mark(state_file, good_article):
    rec = Recorder()

    def failing(text):
        raise PublishError("Telegram odrzucił")

    before = st.load(state_file)
    assert go(state_file, lambda el, i: good_article, rec, send=failing) == 1
    assert st.load(state_file) == before and len(rec.notes) == 1


def test_dry_run_neither_sends_nor_saves(state_file, good_article):
    rec = Recorder()
    before = st.load(state_file)
    assert go(state_file, lambda el, i: good_article, rec, dry_run=True) == 0
    assert rec.sent == [] and st.load(state_file) == before


def test_empty_queue_notifies(state_file, good_article):
    rec = Recorder()
    st.save(state_file, {"published": [{"z": e.z, "symbol": e.symbol, "date": None} for e in ELEMENTS]})
    assert go(state_file, lambda el, i: good_article, rec) == 0
    assert "pusta" in rec.notes[0]


# --- generowanie ---

class FakeClient:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []
        self.messages = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.replies.pop(0)


def resp(text, stop="end_turn"):
    return SimpleNamespace(content=[SimpleNamespace(type="text", text=text)], stop_reason=stop)


def test_generate_two_passes_second_uses_web_search(good_article):
    client = FakeClient([resp(f"<artykul>{good_article}</artykul>"), resp(f"komentarz <artykul>{good_article}!</artykul>")])
    out = generate_article(client, "m", ELEMENTS[25], [])
    assert out.endswith("!")
    assert "tools" not in client.calls[0]
    assert client.calls[1]["tools"][0]["name"] == "web_search"


def test_generate_handles_pause_turn(good_article):
    client = FakeClient([
        resp(f"<artykul>{good_article}</artykul>"),
        resp("<artykul>", stop="pause_turn"),
        resp(f"{good_article}</artykul>"),
    ])
    assert generate_article(client, "m", ELEMENTS[25], []) == good_article


def test_extract_requires_tags():
    with pytest.raises(GenerationError):
        extract_article("sam tekst bez znaczników")


def test_careful_and_hazardous_notes_in_prompt():
    from elementbot.prompts import draft_prompt

    og = next(e for e in ELEMENTS if e.symbol == "Og")
    u = next(e for e in ELEMENTS if e.symbol == "U")
    assert "TRYB OSTROŻNY" in draft_prompt(og, [])
    assert "TEMAT WRAŻLIWY" in draft_prompt(u, [])


# --- sekrety ---

TOKEN = "123456:SECRET-TOKEN"


def test_token_never_leaks_on_network_error(monkeypatch):
    def boom(url, **kw):
        raise requests.ConnectionError(f"failed to connect to {url}")

    monkeypatch.setattr(requests, "post", boom)
    with pytest.raises(PublishError) as exc:
        send_message(TOKEN, "@kanal", "x")
    assert TOKEN not in str(exc.value) and exc.value.__cause__ is None


def test_token_never_leaks_on_api_error(monkeypatch):
    class R:
        status_code = 401
        def json(self):
            return {"ok": False, "description": f"Unauthorized {TOKEN}"}

    monkeypatch.setattr(requests, "post", lambda *a, **k: R())
    with pytest.raises(PublishError) as exc:
        send_message(TOKEN, "@kanal", "x")
    assert TOKEN not in str(exc.value)


def test_send_message_returns_id_and_uses_plain_text(monkeypatch):
    seen = {}

    class R:
        status_code = 200
        def json(self):
            return {"ok": True, "result": {"message_id": 42}}

    def fake(url, json, timeout):
        seen["json"] = json
        return R()

    monkeypatch.setattr(requests, "post", fake)
    assert send_message(TOKEN, "@kanal", "tekst") == 42
    assert "parse_mode" not in seen["json"]
