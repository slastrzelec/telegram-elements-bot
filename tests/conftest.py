import json
from datetime import datetime, timezone

import pytest

GOOD_ARTICLE = """⚙️ Żelazo: metal, na którym stoi cywilizacja 🌍

Gdy bierzesz do ręki zwykły gwóźdź, trzymasz pierwiastek, który ukształtował całe epoki historii. 🔩 Żelazo to czwarty najobficiej występujący pierwiastek w skorupie ziemskiej, a jego jądro należy do najtrwalszych we Wszechświecie. ✨

📜 Ludzie nauczyli się wytapiać żelazo kilka tysięcy lat temu, a epoka żelaza zmieniła rolnictwo, wojny i handel. 🗡️ Pierwsze narzędzia często powstawały z żelaza meteorytowego, spadającego z nieba i zawierającego nikiel, co dla dawnych kowali było prawdziwym cudem. ☄️

🧪 W czystej postaci żelazo jest srebrzystoszare i dość miękkie, ale dodatek węgla zamienia je w stal, czyli materiał twardy i sprężysty. 🏗️ Żelazo łatwo rdzewieje, bo w wilgotnym powietrzu łączy się z tlenem, tworząc uwodnione tlenki, które się łuszczą i odsłaniają kolejne warstwy metalu. 💧

🩸 Żelazo jest też niezbędne życiu. Atom żelaza w hemoglobinie wiąże tlen i roznosi go po całym ciele, dlatego jego niedobór prowadzi do anemii. 🫀 Rośliny, bakterie i zwierzęta potrzebują go w ilościach śladowych, ale regularnie. 🌱

🏭 Dziś żelazo i stal to fundament budownictwa, motoryzacji, maszyn i infrastruktury, a rocznie produkuje się ich ponad miliard ton. 🚗 To nasz najważniejszy metal techniczny i prawdopodobnie jeszcze długo nim pozostanie. 🌉

🎁 Ciekawostka na koniec: gwiazdy produkują pierwiastki lżejsze od żelaza w reakcjach syntezy, ale na żelazie ten proces się kończy, bo dalsze łączenie jąder nie wydziela już energii. ⭐ To właśnie dlatego żelazo bywa nazywane końcem drogi dla gwiezdnych reaktorów. 💫

#Zelazo #Pierwiastki #Chemia #Stal #Historia #Ciekawostki"""


@pytest.fixture
def good_article():
    return GOOD_ARTICLE


@pytest.fixture
def state_file(tmp_path):
    path = tmp_path / "published.json"
    path.write_text(
        json.dumps({"published": [{"z": 13, "symbol": "Al", "date": None, "message_id": None}]}),
        encoding="utf-8",
    )
    return path


def utc(y, m, d, h, mi=0):
    return datetime(y, m, d, h, mi, tzinfo=timezone.utc)
