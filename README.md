# Price Tracker Bot

A small bot that checks a product page on a schedule, stores price/stock
history in SQLite, and sends a Telegram alert when the price drops, rises,
or stock status changes. It runs entirely on **GitHub Actions** — no server,
no hosting costs.

By default it tracks a page on [books.toscrape.com](https://books.toscrape.com),
a sandbox site built specifically for scraping practice, so the project is
safe to demo without worrying about a real store's terms of service.

## How it works

1. A scraper (`tracker/scraper.py`) fetches the target page and parses out
   the title, price, and stock count using BeautifulSoup.
2. The result is compared against the most recent entry in a local SQLite
   database (`tracker/database.py`).
3. If the price or stock status changed, a Telegram message is sent
   (`tracker/notifier.py`).
4. A GitHub Actions workflow (`.github/workflows/check_price.yml`) runs this
   whole flow every 6 hours automatically, and commits the updated database
   back to the repo so your history is preserved.

```
price-tracker-bot/
├── tracker/
│   ├── scraper.py      # fetch + parse the page
│   ├── database.py     # SQLite read/write
│   ├── notifier.py     # send Telegram alert
│   └── main.py         # orchestrates one run
├── tests/
│   ├── test_scraper.py
│   ├── test_database.py
│   └── fixtures/
│       └── sample_page.html   # saved HTML used for offline tests
├── .github/workflows/check_price.yml
├── .env.example
└── requirements.txt
```

## Local setup (Windows / PowerShell)

```powershell
git clone https://github.com/Uchchhas4G3NT52/price-tracker-bot.git
cd price-tracker-bot

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

copy .env.example .env
# then open .env and fill in your Telegram values (see below)
```

Run a single check manually:

```powershell
python -m tracker.main
```

Run the test suite:

```powershell
pytest -v
```

## Setting up Telegram alerts

1. In Telegram, message **@BotFather** and send `/newbot`. Follow the
   prompts to get a bot token (looks like `123456789:ABCdefGhIJKlmNoPQRsTuVwXyZ`).
2. Start a chat with your new bot and send it any message (e.g. "hi") —
   this is required so the bot is allowed to message you back.
3. Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser
   and find your `chat.id` in the JSON response.
4. Put both values in your `.env` file.

If you skip this setup, the bot still runs and logs results to the
console — it just won't send notifications.

## Enabling the automated schedule on GitHub

The workflow needs your Telegram credentials as **repository secrets**
(never commit them to `.env`):

1. On GitHub: **Settings → Secrets and variables → Actions → New repository secret**
2. Add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
3. (Optional) Add a repository **variable** named `TARGET_URL` if you want
   to track a different product page than the default.
4. Push to GitHub — the workflow will start running automatically every
   6 hours, and you can also trigger it manually from the **Actions** tab
   using "Run workflow".

## Testing approach

Tests never hit the live website. `tests/fixtures/sample_page.html` is a
saved snapshot of a real product page, so `test_scraper.py` checks the
parsing logic against fixed, known content — fast, reliable, and immune to
the real site changing or going down. `test_database.py` uses pytest's
`tmp_path` fixture to create a throwaway SQLite file per test, so tests
never touch your real `price_history.db`.

## Possible extensions

- Track multiple products by looping over a list of URLs
- Add a `--once` vs `--watch` CLI mode using `argparse`
- Plot price history over time with `matplotlib`
- Swap Telegram for email alerts via `smtplib`
