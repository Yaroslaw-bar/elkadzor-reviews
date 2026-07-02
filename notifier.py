import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram не настроен: отсутствуют TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }
    try:
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")
        return False


def notify_new_reviews(reviews, source_names):
    if not reviews:
        return
    count = len(reviews)
    header = f"🔔 <b>Новые отзывы: {count}</b>\n\n"
    lines = []
    for r in reviews[:10]:
        source_name = source_names.get(r[1], r[1])
        author = r[3] or "Аноним"
        rating = f" • {r[4]}/5" if r[4] else ""
        text = (r[5] or "")[:180]
        if len(r[5]) > 180:
            text += "…"
        lines.append(f"<b>{source_name}</b> • {author}{rating}\n{text}\n")
    if count > 10:
        lines.append(f"…и ещё {count - 10} отзывов")
    message = header + "\n".join(lines)
    send_telegram_message(message)
