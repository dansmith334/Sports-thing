# Sports Arbitrage Alert Bot (Python MVP)

A beginner-friendly Python bot that scans **pregame moneyline** odds from **The Odds API**, checks for possible arbitrage opportunities, and sends **Telegram alerts**.

> This MVP **does not place bets**. It only scans and alerts.

## Features

- Uses official APIs only:
  - The Odds API for odds data
  - Telegram Bot API for alert delivery
- Sports supported:
  - NBA
  - NFL
  - MLB
  - NHL
- Markets supported:
  - Pregame moneyline (`h2h`)
- Converts American odds to decimal
- Calculates implied probability totals
- Detects arbitrage when implied probability sum is below `1.00`
- Filters by minimum edge (`MIN_ARB_PERCENT`)
- Calculates suggested stake split using `TOTAL_STAKE`
- Stores sent alerts in SQLite to avoid duplicate messages
- Prints normal scan logs to terminal
- Includes unit tests for core math logic

---

## Project structure

- `main.py`
- `config.py`
- `odds_api.py`
- `arbitrage.py`
- `telegram_alerts.py`
- `database.py`
- `requirements.txt`
- `.env.example`
- `tests/`

---

## macOS setup (exact steps)

### 1) Install Python 3

On macOS, verify Python:

```bash
python3 --version
```

If needed, install from [python.org](https://www.python.org/downloads/mac-osx/) or Homebrew.

### 2) Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Create your `.env` file

Copy the example file:

```bash
cp .env.example .env
```

Then edit `.env` with your real values:

- `ODDS_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `REFRESH_SECONDS`
- `MIN_ARB_PERCENT`
- `TOTAL_STAKE`
- `REGIONS`

Example:

```env
ODDS_API_KEY=abcd1234
TELEGRAM_BOT_TOKEN=123456:ABCDEF...
TELEGRAM_CHAT_ID=123456789
REFRESH_SECONDS=60
MIN_ARB_PERCENT=0.5
TOTAL_STAKE=100
REGIONS=us
```

---

## Telegram setup

### 1) Create a bot with BotFather

1. Open Telegram and search for **@BotFather**.
2. Send `/newbot`.
3. Follow prompts.
4. Copy the bot token into `TELEGRAM_BOT_TOKEN`.

### 2) Find your chat ID

1. Start a chat with your bot and send a test message (for example: `hello`).
2. Open this URL in your browser (replace token):

```text
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

3. In the JSON response, find `message.chat.id`.
4. Put that number in `TELEGRAM_CHAT_ID`.

---

## Run the bot

```bash
python3 main.py
```

Behavior:

- Runs forever in a loop.
- Every `REFRESH_SECONDS`, it fetches odds for NBA/NFL/MLB/NHL.
- Prints what it is checking.
- Sends Telegram alerts if qualifying arbitrage is found.
- Prints `No opportunities found.` when none are found.
- Handles API errors gracefully and continues.

---

## Run tests

```bash
pytest
```

---

## Telegram alert format

The message includes:

- Sport
- Event
- Start time
- Market
- Best prices and sportsbooks
- Implied probability total
- Estimated edge
- Suggested stake split
- A manual verification warning

---

## Common errors and fixes

### Error: `Missing required environment variable: ...`

Your `.env` is missing a required key. Add the variable and restart.

### Error: Odds API request failed

- Check internet connection.
- Check `ODDS_API_KEY` is valid.
- Confirm your plan includes requested sports/regions.
- Reduce request frequency if you hit rate limits.

### Error: Failed to send Telegram message

- Check `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
- Make sure you started a conversation with the bot.
- Send another test message and re-check `getUpdates`.

### No opportunities found repeatedly

This is normal. Arbitrage is rare and odds move fast.

---

## Notes for beginners

- Start with small refresh intervals like `60` seconds to avoid too many API calls.
- Keep this as an **alerting tool only**.
- Always verify odds, limits, and market rules manually before any action.
