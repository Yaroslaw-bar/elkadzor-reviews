import os
import re
import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st

from config import SOURCES
from db import get_reviews, get_stats


_MONTHS_EN = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

_POSITIVE_WORDS = {
    "отлично", "хорошо", "прекрасно", "замечательно", "супер", "класс", "круто",
    "рекомендую", "советую", "доволен", "довольна", "довольны", "благодарю", "спасибо",
    "качество", "надежно", "аккуратно", "оперативно", "быстро", "вежливо",
    "профессионально", "понравилось", "рад", "рады", "высокое качество", "отличное качество",
    "хороший", "хорошая", "хорошие", "хорошее", "отличный", "отличная", "отличные",
    "крутая", "крутой", "великолепно", "надеюсь", "прослужит", "рекомендация",
}

_NEGATIVE_WORDS = {
    "плохо", "ужасно", "отвратительно", "неудачно", "разочарован", "разочарована",
    "разочарованы", "ошибка", "ошибки", "проблема", "проблемы", "дефект", "дефекты",
    "некачественно", "неаккуратно", "грубо", "хамство", "поздно", "задержка",
    "переносили", "перенесли", "не доделали", "криво", "косо", "трещины", "ржавчина",
    "не рекомендую", "не советую", "обман", "обманули", "жалоба", "недоволен",
    "недовольна", "недовольны", "плохой", "плохая", "плохие", "ненадежно", "вранье",
    "халтура", "испортили", "сломалось", "отказал", "требую", "возврат",
}

_NEGATIONS = {
    "не", "нет", "без", "ни", "никак", "ничего", "неочень", "не очень",
}

_POSITIVE_EMOJI = {":)", ":-)", "😊", "😍", "👍", "❤", "💪", "🙏"}
_NEGATIVE_EMOJI = {":(", ":-(", "😞", "😠", "👎", "🤬", "😡", "💩"}




def _analyze_sentiment(text, rating):
    if not text:
        return "нейтральный"
    lower = text.lower()
    score = 0
    negative_hits = 0
    positive_hits = 0
    words = re.findall(r"[а-яa-z0-9]+(?:\-[а-яa-z0-9]+)?", lower)
    for i, word in enumerate(words):
        weight = 1
        if i > 0 and words[i - 1] in _NEGATIONS:
            weight = -1
        if word in _POSITIVE_WORDS:
            score += weight
            positive_hits += 1
        elif word in _NEGATIVE_WORDS:
            score -= weight
            negative_hits += 1

    for emoji in _POSITIVE_EMOJI:
        if emoji in text:
            score += 1
            positive_hits += 1
    for emoji in _NEGATIVE_EMOJI:
        if emoji in text:
            score -= 1
            negative_hits += 1

    if rating is not None and not pd.isna(rating):
        if rating >= 4.5:
            score += 2
        elif rating >= 4:
            score += 1
        elif rating <= 2:
            score -= 2
            negative_hits += 1
        elif rating < 4:
            score -= 1

    if negative_hits == 0 and score > 0:
        return "положительный"
    if positive_hits == 0 and negative_hits > 0 and score < 0:
        return "отрицательный"
    if score > 0:
        return "положительный"
    if score < 0:
        return "отрицательный"
    return "нейтральный"


def _recommendation(sentiment):
    if sentiment == "положительный":
        return (
            "Рекомендация: поблагодарите клиента за отзыв, отметьте, что рады качественной работе, "
            "и пригласите обратиться снова."
        )
    if sentiment == "отрицательный":
        return (
            "Рекомендация: извинитесь за неудобства, скажите, что мы обязательно разберёмся "
            "и исправим ситуацию. Попросите связаться по телефону или оставить контакты."
        )
    return "Рекомендация: ответьте клиенту кратко и вежливо, уточните детали при необходимости."


def _sentiment_badge(sentiment):
    colors = {
        "положительный": "🟢 Положительный",
        "нейтральный": "🟡 Нейтральный",
        "отрицательный": "🔴 Отрицательный",
    }
    return colors.get(sentiment, sentiment)


def _parse_date(value):
    if pd.isna(value) or value is None:
        return None
    text = str(value).strip()
    patterns = [
        (r"(\d{2})\.(\d{2})\.(\d{4})", lambda m: f"{m.group(3)}-{m.group(2)}-{m.group(1)}"),
        (r"(\d{4})-(\d{2})-(\d{2})", lambda m: f"{m.group(1)}-{m.group(2)}-{m.group(3)}"),
    ]
    for pattern, formatter in patterns:
        m = re.match(pattern, text)
        if m:
            try:
                return datetime.strptime(formatter(m), "%Y-%m-%d")
            except ValueError:
                continue
    month_map = {
        "january": "01", "february": "02", "march": "03", "april": "04",
        "may": "05", "june": "06", "july": "07", "august": "08",
        "september": "09", "october": "10", "november": "11", "december": "12",
    }
    m = re.match(r"([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})", text)
    if m:
        month = month_map.get(m.group(1).lower())
        if month:
            try:
                return datetime.strptime(f"{m.group(3)}-{month}-{m.group(2).zfill(2)}", "%Y-%m-%d")
            except ValueError:
                return None
    return None


def _format_date(dt):
    if dt is None:
        return ""
    return f"{_MONTHS_EN[dt.month - 1]} {dt.day}, {dt.year}"


st.set_page_config(page_title="Elkadzor Review Monitor", layout="wide")

st.title("Мониторинг отзывов — Элькадор")

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reviews.db")
conn = sqlite3.connect(db_path)

raw_stats = get_stats(conn)
active_sources = {row[0] for row in raw_stats}
source_options = ["Все"] + [SOURCES[s]["name"] for s in active_sources if s in SOURCES]
source_filter = st.sidebar.selectbox("Площадка", source_options)
selected_key = None
if source_filter != "Все":
    selected_key = next((k for k, v in SOURCES.items() if v["name"] == source_filter), None)

sort_by = st.sidebar.selectbox("Сортировка", ["По дате", "По оценке", "По тональности"])
sort_order = st.sidebar.radio("Порядок", ["По убыванию", "По возрастанию"], index=0)

st.sidebar.markdown("---")
date_range = st.sidebar.date_input(
    "Диапазон дат",
    value=(datetime(2012, 1, 1), datetime.now()),
    min_value=datetime(2012, 1, 1),
    max_value=datetime.now(),
)
use_date_range = st.sidebar.checkbox("Фильтровать по диапазону дат")


def _stars(rating):
    if rating is None or pd.isna(rating):
        return "—"
    full = int(rating)
    half = 1 if rating - full >= 0.5 else 0
    empty = 5 - full - half
    return "★" * full + "⯨" * half + "☆" * empty


if raw_stats:
    st.subheader("Статистика по площадкам")
    cols = st.columns(len(raw_stats))
    for col, (source, count, avg_rating) in zip(cols, raw_stats):
        name = SOURCES.get(source, {}).get("name", source)
        rating_text = f"{_stars(avg_rating)} {avg_rating:.2f}/5" if avg_rating else "—"
        col.metric(name, f"{count} отзывов", rating_text)

st.subheader("Все отзывы")
reviews = get_reviews(conn, source=selected_key)
df = pd.DataFrame(
    reviews,
    columns=["id", "source", "author", "date", "rating", "text", "url", "fetched_at", "is_new"],
)
if not df.empty:
    df["source"] = df["source"].map(lambda s: SOURCES.get(s, {}).get("name", s))
    df = df[["source", "author", "date", "rating", "text", "fetched_at"]]

    df["date_parsed"] = df["date"].apply(_parse_date)
    if use_date_range and isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        df = df[df["date_parsed"].apply(lambda dt: dt is not None and start_date <= dt.date() <= end_date)]

    df["sentiment"] = df.apply(lambda row: _analyze_sentiment(row["text"], row["rating"]), axis=1)
    sentiment_order = {"положительный": 1, "нейтральный": 2, "отрицательный": 3}
    df["sentiment_rank"] = df["sentiment"].map(sentiment_order)

    if sort_by == "По дате":
        df = df.sort_values("date_parsed", ascending=(sort_order == "По возрастанию"), na_position="last")
    elif sort_by == "По оценке":
        df = df.sort_values("rating", ascending=(sort_order == "По возрастанию"), na_position="last")
    else:
        df = df.sort_values("sentiment_rank", ascending=(sort_order == "По возрастанию"), na_position="last")
    df["date"] = df["date_parsed"].apply(_format_date)
    df = df.drop(columns=["date_parsed", "sentiment_rank"])

    csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        "Экспорт CSV",
        csv_bytes,
        "reviews.csv",
        "text/csv",
    )

    for _, row in df.iterrows():
        rating_text = f"{_stars(row['rating'])}" if pd.notna(row["rating"]) else "—"
        with st.expander(f"{row['source']} • {row['author']} • {rating_text} • {row['date']}", expanded=True):
            st.write(row["text"])
            st.markdown(f"**{_sentiment_badge(row['sentiment'])}**")
            st.info(_recommendation(row['sentiment']))
            col1, col2 = st.columns([1, 1])
            with col2:
                st.caption(f"Собрано: {row['fetched_at'][:10]}")
else:
    st.info("Отзывов пока нет. Запусти scheduler.py для сбора данных.")

conn.close()
