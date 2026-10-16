import json

from elementbot import state as st
from elementbot.elements import ELEMENTS
from elementbot.queue import next_element
from elementbot.timegate import should_publish_now

from conftest import utc


def test_118_unique_elements_in_order():
    assert len(ELEMENTS) == 118
    assert [e.z for e in ELEMENTS] == list(range(1, 119))
    assert len({e.symbol for e in ELEMENTS}) == 118


def test_seeded_state_skips_already_written_elements():
    data = json.load(open("data/published.json", encoding="utf-8"))
    done = st.published_numbers(data)
    assert done == {13, 15, 29, 33, 34, 80, 83}
    seen = []
    while True:
        el = next_element(data)
        if el is None or len(seen) >= 12:
            break
        seen.append(el.symbol)
        st.mark_published(data, el.z, el.symbol, "2026-01-01", 1)
    assert seen[:6] == ["H", "He", "Li", "Be", "B", "C"]
    assert "Al" not in seen and "P" not in seen


def test_queue_exhausts():
    data = {"published": [{"z": e.z, "symbol": e.symbol, "date": None} for e in ELEMENTS]}
    assert next_element(data) is None


def test_state_roundtrip_is_atomic(tmp_path):
    p = tmp_path / "s.json"
    st.save(p, {"published": []})
    data = st.load(p)
    st.mark_published(data, 1, "H", "2026-10-17", 5)
    st.save(p, data)
    assert st.load(p)["published"][0]["symbol"] == "H"
    assert not list(tmp_path.glob(".state-*"))


def test_timegate_summer_8_local_is_06_utc():
    data = {"published": []}
    assert should_publish_now(utc(2026, 7, 1, 6, 5), data)  # 8:05 CEST
    assert not should_publish_now(utc(2026, 7, 1, 5, 55), data)  # 7:55 CEST


def test_timegate_winter_8_local_is_07_utc():
    data = {"published": []}
    assert not should_publish_now(utc(2026, 12, 1, 6, 5), data)  # 7:05 CET
    assert should_publish_now(utc(2026, 12, 1, 7, 5), data)  # 8:05 CET


def test_timegate_only_once_per_day():
    data = {"published": [{"z": 1, "symbol": "H", "date": "2026-07-01"}]}
    assert not should_publish_now(utc(2026, 7, 1, 7, 5), data)  # drugi cron tego dnia
    assert should_publish_now(utc(2026, 7, 2, 6, 5), data)  # następny dzień


def test_timegate_window_closes_at_noon():
    data = {"published": []}
    assert should_publish_now(utc(2026, 7, 1, 9, 59), data)  # 11:59 CEST
    assert not should_publish_now(utc(2026, 7, 1, 10, 0), data)  # 12:00 CEST
