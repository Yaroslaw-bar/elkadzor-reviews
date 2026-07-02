import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from config import SOURCES, HEADERS
from dynamic_parser import parse_2gis, parse_remkarta, parse_yandex, parse_zoon


def fetch(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"Ошибка загрузки {url}: {e}")
        return ""


def _rate_from_stars(rate_tag):
    if not rate_tag:
        return None
    full = len(rate_tag.select(".icon-star"))
    half = len(rate_tag.select(".icon-star-half-alt"))
    empty = len(rate_tag.select(".icon-star-empty"))
    total = full + half + empty
    if total == 0:
        return None
    return full + half * 0.5


def parse_site_elcador():
    url = SOURCES["site"]["url"]
    html = fetch(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "lxml")
    reviews = []
    for item in soup.select(".comments .item"):
        text_tag = item.select_one(".txt")
        author_tag = item.select_one(".autor")
        date_tag = item.select_one(".date")
        rate_tag = item.select_one(".rate")
        text = text_tag.get_text(" ", strip=True) if text_tag else ""
        if not text:
            continue
        author = author_tag.get_text(strip=True) if author_tag else None
        date = date_tag.get_text(strip=True) if date_tag else None
        rating = _rate_from_stars(rate_tag)
        reviews.append({
            "source": "site",
            "author": author,
            "date": date,
            "rating": rating,
            "text": text,
            "url": url,
        })
    return reviews


def _generic_review_block(soup, source_key):
    url = SOURCES[source_key]["url"]
    reviews = []
    candidates = soup.find_all(attrs={"class": lambda x: x and "review" in x.lower()})
    for item in candidates:
        text_tag = item.select_one(".review-text, .text, [class*='message'], [class*='content']")
        if not text_tag:
            ps = item.find_all("p")
            if ps:
                text_tag = ps[0]
        author_tag = item.select_one(".review-author, .author, .name, [class*='user']")
        date_tag = item.select_one(".review-date, .date, time, [class*='time']")
        if not text_tag:
            continue
        text = text_tag.get_text(" ", strip=True)
        if len(text) < 20:
            continue
        author = author_tag.get_text(strip=True) if author_tag else None
        date = None
        if date_tag:
            date = date_tag.get("datetime") or date_tag.get_text(strip=True)
        reviews.append({
            "source": source_key,
            "author": author,
            "date": date,
            "rating": None,
            "text": text,
            "url": url,
        })
    return reviews


def parse_plaso():
    url = SOURCES["plaso"]["url"]
    html = fetch(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "lxml")
    reviews = []
    for item in soup.select(".review"):
        text_tag = item.select_one(".review_text")
        if not text_tag:
            continue
        text = text_tag.get_text(" ", strip=True)
        if len(text) < 10:
            continue
        author_tag = item.select_one(".font-weight-bold")
        date_tag = item.select_one(".review_time")
        stars_tag = item.select_one(".reviews-stars")
        author = author_tag.get_text(strip=True) if author_tag else None
        date = date_tag.get_text(strip=True) if date_tag else None
        rating = None
        if stars_tag:
            full = len(stars_tag.select(".yellow"))
            empty = len(stars_tag.select(".gray"))
            total = full + empty
            if total:
                rating = full
        reviews.append({
            "source": "plaso",
            "author": author,
            "date": date,
            "rating": rating,
            "text": text,
            "url": url,
        })
    return reviews


def parse_all():
    result = {
        "site": parse_site_elcador(),
        "plaso": parse_plaso(),
        "2gis": parse_2gis(),
        "remkarta": parse_remkarta(),
        "yandex": parse_yandex(),
        "zoon": parse_zoon(),
    }
    return result
