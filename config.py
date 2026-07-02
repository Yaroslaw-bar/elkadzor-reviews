import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "reviews.db"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SOURCES = {
    "site": {
        "name": "Сайт Элькадор",
        "url": "https://elcador.ru/otzyvy/",
        "type": "static",
    },
    "2gis": {
        "name": "2GIS",
        "url": "https://2gis.ru/spb/search/%D0%AD%D0%BB%D1%8C%D0%BA%D0%B0%D0%B4%D0%BE%D1%80/firm/70000001045099352/30.317373%2C59.868214/tab/reviews",
        "type": "dynamic",
    },
    "plaso": {
        "name": "Plaso.pro",
        "url": "https://plaso.pro/place/209775",
        "type": "static",
    },
    "remkarta": {
        "name": "RemKarta",
        "url": "https://spb.remkarta.ru/sankt-peterburg/elkador-580029/",
        "type": "dynamic",
    },
    "yandex": {
        "name": "Яндекс.Карты",
        "url": "https://yandex.ru/maps/org/elkador/114479500627/reviews/",
        "type": "dynamic",
    },
    "zoon": {
        "name": "Zoon",
        "url": "https://zoon.ru/spb/building/ofis_prodazh_elkador/",
        "type": "dynamic",
    },
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
