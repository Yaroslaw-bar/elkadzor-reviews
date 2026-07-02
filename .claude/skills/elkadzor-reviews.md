# Elkadzor Review Monitor

Skill for working with the Elkadzor Review Monitor project — a local Python tool that collects, stores, notifies about, and visualizes customer reviews for the «Элькадор» company.

## When to use

Use this skill when the user asks about the `elkadzor-reviews` project, wants to run the dashboard, add a new review source, fix parsers, schedule collection, export data, or deploy the project.

## Project layout

- `project/config.py` — review sources, HTTP headers, environment variables
- `project/parser.py` — static HTML parsers (Elkadzor site)
- `project/dynamic_parser.py` — Playwright parsers (Yandex Maps)
- `project/db.py` — SQLite storage layer
- `project/notifier.py` — Telegram notifications
- `project/scheduler.py` — APScheduler wrapper
- `project/dashboard.py` — Streamlit dashboard
- `project/collect_reviews.py` — manual collection entry point

## Common commands

Install dependencies:

```powershell
cd C:\project\elkadzor-reviews\project
.\.venv\Scripts\pip install -r requirements.txt
```

Run collection:

```powershell
.\.venv\Scripts\python collect_reviews.py
```

Run dashboard:

```powershell
$env:STREAMLIT_SERVER_HEADLESS="true"
.\.venv\Scripts\python -m streamlit run dashboard.py
```

Run scheduler:

```powershell
.\.venv\Scripts\python -c "from scheduler import start_scheduler; start_scheduler(24)"
```

## Adding a new source

1. Add source to `config.py` with `"type": "static"` or `"dynamic"`.
2. Implement parser in `parser.py` (static) or `dynamic_parser.py` (dynamic).
3. Register parser in `collect_reviews.py` `parsers` dict.
4. Add source key to `ACTIVE_SOURCES` in `collect_reviews.py`.
5. Update `README.md` supported-platforms table.

## Notes

- The repo root contains only `README.md` and project metadata; source code lives in `project/`.
- `.env` is required for Telegram notifications.
- `reviews.db` is not tracked by git.
- Dashboard runs at `http://localhost:8501` by default.
