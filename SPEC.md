# Specyfikacja: bot kanału o pierwiastkach (v1)

## Cel
Codziennie o 8:00 czasu polskiego bot publikuje na kanale Telegram jeden artykuł popularnonaukowy o kolejnym pierwiastku chemicznym, w ustalonym stylu, bez udziału człowieka.

## Zakres v1
W zakresie: kolejka 118 pierwiastków, generowanie, weryfikacja faktów, walidacja formatu, publikacja, powiadomienie właściciela o błędzie, harmonogram.
Poza zakresem: obrazki, panel, wiele kanałów, analiza zasięgów.

## Przepływ
1. Bramka czasu: działanie tylko gdy w Warszawie jest godzina 8-11 i dziś jeszcze nic nie opublikowano.
2. Kolejka: następny pierwiastek wg liczby atomowej, z pominięciem już opublikowanych (stan w `data/published.json`, zasiane: Al, P, Cu, As, Se, Hg, Bi).
3. Szkic: model pisze artykuł wg promptu stylu.
4. Weryfikacja: drugie wywołanie z wyszukiwarką sieciową sprawdza daty, liczby, nazwiska; niepotwierdzone twierdzenia usuwa lub łagodzi.
5. Walidacja (deterministyczna, bez modelu): brak Markdown, zakazane hashtagi, brak linku do kanału, emoji w każdym akapicie, sekcja "Ciekawostka na koniec", linia hashtagów, limit znaków.
6. Do 3 prób. Błędy walidacji wracają do modelu jako uwagi.
7. Po sukcesie: publikacja i natychmiastowy zapis stanu. Po porażce: brak publikacji i wiadomość do właściciela z powodem.

## Styl (egzekwowany promptem i walidatorem)
Polski, jeden płynny tekst, tytuł z emoji, historia i odkrywca, budowa i właściwości, zastosowania, "Ciekawostka na koniec", linia hashtagów. Zero składni Markdown. Gęste emoji. Tekst krótki (ok. 1800-3000 znaków). Zakazane hashtagi: #edukacja #magnesy #przyroda #GFP #biofluorescencja #nauka. Bez linku do kanału.

## Bezpieczeństwo
- Sekrety (`ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL`, `OWNER_CHAT_ID`) wyłącznie w sekretach GitHub Actions. Nigdy w repo, logach ani komunikatach błędów (token jest wycinany z błędów sieciowych).
- Repo prywatne. Brak śladów narzędzi AI w commitach i dokumentacji. Commity stanu wykonuje konto `elements-bot`.
- Pierwiastki groźne (m.in. U, Pu, Po, Tl, Cd, Pb, Be, Np, Am, Cm): wyłącznie historia, mechanizm działania i kontekst. Bez syntezy, pozyskiwania, proporcji i instrukcji. Dotyczy wszystkich artykułów.
- Uprawnienia workflow: tylko `contents: write` (zapis stanu).
- Bot publikuje wyłącznie na kanale z konfiguracji. Nie przyjmuje poleceń z Telegrama.

## Ryzyka (znane i nierozwiązane w v1)
- Weryfikacja zmniejsza, ale nie eliminuje błędów merytorycznych. Pierwiastki egzotyczne (m.in. Pm, At, Fr, Z >= 99) mają tryb ostrożny: krótszy tekst, mało liczb, jawne zastrzeżenia.
- Jeśli publikacja się uda, a zapis stanu w repo nie, następnego dnia powtórzy się ten sam pierwiastek. Zapis stanu jest krokiem `always()`, ale to ryzyko szczątkowe.
- Nazwa narzędzia wyszukiwarki w API i sposób rozliczania muszą zostać potwierdzone przy pierwszym prawdziwym uruchomieniu (testy używają atrap).
- Harmonogram GitHub Actions może się opóźnić o kilkanaście minut.
- Cron działa w UTC. Dwa wyzwalacze (06:00 i 07:00 UTC) + bramka czasu dają 8:00 latem i zimą.
- Kolejka kończy się po 118 pierwiastkach; bot wyśle wtedy wiadomość do właściciela.

## Kryteria akceptacji
- Testy jednostkowe przechodzą (kolejka, bramka czasu, walidator, stan, przepływ główny, brak wycieku tokena).
- Tryb `DRY_RUN` generuje artykuł bez publikacji i bez zapisu stanu.
