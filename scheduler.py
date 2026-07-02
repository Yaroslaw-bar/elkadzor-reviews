import sys
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from apscheduler.schedulers.background import BackgroundScheduler

from config import SOURCES
from db import init_db, insert_review, get_new_reviews, mark_all_seen
from notifier import notify_new_reviews
from parser import parse_all


def run_check():
    print("Начинаю проверку отзывов…")
    conn = init_db()
    parsed = parse_all()
    added = 0
    for source_key, reviews in parsed.items():
        for r in reviews:
            row_id = insert_review(conn, r["source"], r["author"], r["date"], r["rating"], r["text"], r["url"])
            if row_id:
                added += 1
    if added:
        new_reviews = get_new_reviews(conn)
        notify_new_reviews(new_reviews, {k: v["name"] for k, v in SOURCES.items()})
        mark_all_seen(conn)
        print(f"Добавлено новых отзывов: {added}")
    else:
        print("Новых отзывов не найдено")
    conn.close()


def start_scheduler(interval_hours=24):
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_check, "interval", hours=interval_hours)
    scheduler.start()
    print(f"Планировщик запущен. Интервал: {interval_hours} ч")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
        print("Планировщик остановлен")


if __name__ == "__main__":
    run_check()
