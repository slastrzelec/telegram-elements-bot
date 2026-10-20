# elementy-bot

Bot publikujący codziennie (docelowo rano, w oknie 8:00-21:59 czasu polskiego) artykuł popularnonaukowy o kolejnym pierwiastku na kanale Telegram. Pełna specyfikacja: [SPEC.md](SPEC.md).

## Uruchomienie lokalne (bez publikacji)

```
cd elementy-bot
pip install -r requirements-dev.txt
DRY_RUN=1 ANTHROPIC_API_KEY=... python -m elementbot
# albo przez subskrypcję (wymaga zainstalowanego CLI: npm i -g @anthropic-ai/claude-code):
DRY_RUN=1 CLAUDE_CODE_OAUTH_TOKEN=... python -m elementbot
```

`DRY_RUN=1` generuje artykuł i wypisuje go na ekran, bez wysyłki i bez zapisu stanu. `FORCE=1` pomija bramkę czasu.

## Sekrety (GitHub Actions)

Jedno z dwóch: `CLAUDE_CODE_OAUTH_TOKEN` (subskrypcja; token z komendy `claude setup-token`) albo `ANTHROPIC_API_KEY` (rozliczenie API). Oraz: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL` (np. `@nazwa_kanalu`), `OWNER_CHAT_ID` (do powiadomień o błędach; właściciel musi wcześniej napisać do bota).

## Testy

```
cd elementy-bot
python -m pytest
```

Co jest sprawdzane: kompletność i kolejność 118 pierwiastków; kolejka i pomijanie już opisanych; bramka czasu w lecie i zimie oraz publikacja raz dziennie; walidator formatu (Markdown, zakazane hashtagi, emoji w każdym akapicie, długość, sekcja końcowa); przepływ główny (retry, powiadomienia, brak zapisu stanu po błędzie, tryb DRY_RUN); dwuetapowe generowanie z atrapą API i z atrapą CLI (flagi, blokada narzędzi, usuwanie klucza API z otoczenia, błędy i limity czasu); brak wycieku tokena w błędach.

Czego nie sprawdzają: prawdziwego API modelu i prawdziwego Telegrama (używane są atrapy), merytorycznej poprawności wygenerowanych artykułów, zachowania harmonogramu GitHub Actions.
