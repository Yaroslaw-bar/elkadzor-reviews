"""
Сбор новых отзывов с активных площадок и обновление базы дашборда.

Работает с сайтом Элькадор и Яндекс.Картами.
"""
import sys
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from config import SOURCES
from db import init_db, insert_review, get_new_reviews, mark_all_seen
from dynamic_parser import parse_yandex
from notifier import notify_new_reviews
from parser import parse_site_elcador


ACTIVE_SOURCES = ["site", "yandex"]


def collect():
    print(f"[{datetime.now().isoformat()}] Начинаю сбор отзывов...")
    conn = init_db()

    parsers = {
        "site": parse_site_elcador,
        "yandex": parse_yandex,
    }

    total_found = 0
    total_added = 0

    for key in ACTIVE_SOURCES:
        parser = parsers.get(key)
        if not parser:
            continue

        name = SOURCES[key]["name"]
        try:
            reviews = parser()
        except Exception as e:
            print(f"  ✗ {name}: ошибка — {e}")
            continue

        added = 0
        for r in reviews:
            row_id = insert_review(
                conn,
                r["source"],
                r["author"],
                r["date"],
                r["rating"],
                r["text"],
                r["url"],
            )
            if row_id:
                added += 1

        print(f"  • {name}: найдено {len(reviews)}, добавлено {added}")
        total_found += len(reviews)
        total_added += added

    if total_added:
        new_reviews = get_new_reviews(conn)
        notify_new_reviews(new_reviews, {k: v["name"] for k, v in SOURCES.items()})
        mark_all_seen(conn)
        print(f"\nДобавлено новых отзывов: {total_added}")
    else:
        print("\nНовых отзывов не найдено.")

    conn.close()


if __name__ == "__main__":
    collect()
