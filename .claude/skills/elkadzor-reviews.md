# Elkadzor Review Monitor — Claude Code skill

Skill for working with the `elkadzor-reviews` repository: a local Python MVP that monitors customer reviews for the «Элькадор» company across multiple platforms, notifies via Telegram and visualizes data in a Streamlit dashboard.

## When to use

Use this skill when the user wants to:

- understand the project structure;
- run the dashboard, collection or scheduler;
- add a new review source or fix an existing parser;
- update `README.md` or prepare the project for publication;
- check for runtime errors, export data or deploy the project;
- make any code change inside `project/`.

## Project layout

Repository root:

- `README.md` — project overview, install/run instructions, supported platforms
- `project/` — all source code
  - `config.py` — review sources (`SOURCES`), HTTP headers, env variables
  - `parser.py` — static HTML parsers (Elkadzor site)
  - `dynamic_parser.py` — Playwright-based parsers (Yandex Maps)
  - `db.py` — SQLite initialization, reads, writes
  - `notifier.py` — Telegram bot notifications
  - `scheduler.py` — APScheduler wrapper
  - `dashboard.py` — Streamlit dashboard
  - `collect_reviews.py` — manual collection entry point
  - `requirements.txt` — Python dependencies
  - `.env.example` — template for secrets
- `.claude/skills/elkadzor-reviews.md` — this skill

## Environment

- Windows PowerShell is the primary shell.
- Python virtual environment is at `project/.venv/`. All Python commands must use it.
- Database `project/reviews.db` is local and not tracked by git.
- Telegram notifications require `project/.env` with `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.

## Common commands

Always run commands from `C:\project\elkadzor-reviews\project` unless noted.

Install or update dependencies:

```powershell
cd C:\project\elkadzor-reviews\project
.\.venv\Scripts\pip install -r requirements.txt
```

Run one-time review collection:

```powershell
.\.venv\Scripts\python collect_reviews.py
```

Run Streamlit dashboard (background-friendly):

```powershell
$env:STREAMLIT_SERVER_HEADLESS="true"
.\.venv\Scripts\python -m streamlit run dashboard.py
```

Run scheduler for periodic collection:

```powershell
.\.venv\Scripts\python -c "from scheduler import start_scheduler; start_scheduler(24)"
```

Check database contents:

```powershell
.\.venv\Scripts\python -c "import sqlite3; conn=sqlite3.connect('reviews.db'); cur=conn.cursor(); cur.execute('SELECT source, COUNT(*) FROM reviews GROUP BY source'); [print(r) for r in cur.fetchall()]; conn.close()"
```

## How to make changes

1. Read the relevant file(s) first.
2. Keep changes minimal — the user prefers working MVP over architecture "for the future".
3. Update `README.md` if the change affects install/run steps, supported platforms or project structure.
4. Run the affected script or dashboard locally after the change.
5. Commit and push with a concise message describing the fix/feature.

## Adding or fixing a review source

1. Add source to `config.py` with `"type": "static"` or `"dynamic"`.
2. Implement parser in `parser.py` (static) or `dynamic_parser.py` (dynamic). Return a list of dicts with keys: `source`, `author`, `date`, `rating`, `text`, `url`.
3. Register the parser in `collect_reviews.py` under the `parsers` dict.
4. Add the source key to `ACTIVE_SOURCES` in `collect_reviews.py` if it should run regularly.
5. Update the supported-platforms table in `README.md`.
6. Test with `collect_reviews.py`.

## Pre-publication checklist

Before considering the project ready to show:

- `README.md` is up to date and has no broken paths.
- Code is committed and pushed.
- Temporary files (screenshots, `test_export.csv`, `.venv`, `__pycache__`, `reviews.db`) are not staged.
- The dashboard starts and health endpoint returns `ok`.
- CSV export produces a readable file.

## Notes

- Keep the Russian language and tone already established in the UI and README.
- Do not delete, rename or move files without explicit permission.
- Do not publish posts or send messages on behalf of the user.
- Avoid long introductions and final summaries in responses; report only what changed.
