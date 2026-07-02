"""
Динамические источники отзывов, которые требуют браузера.
"""
import re
import time

from playwright.sync_api import sync_playwright

from config import SOURCES


def _browse(url, wait_ms=4000):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            time.sleep(wait_ms / 1000)
            html = page.content()
            return html
        finally:
            browser.close()


def parse_2gis():
    url = SOURCES["2gis"]["url"]
    html = _browse(url, wait_ms=5000)
    if not html:
        return []
    if "captcha" in html.lower():
        print("2GIS: требуется капча — отзывы не собраны")
        return []
    return _generic_from_html(html, "2gis", url)


def parse_remkarta():
    url = SOURCES["remkarta"]["url"]
    html = _browse(url, wait_ms=4000)
    if not html:
        return []
    return _generic_from_html(html, "remkarta", url)


def parse_yandex():
    url = SOURCES["yandex"]["url"]
    html = _browse(url, wait_ms=5000)
    if not html:
        return []
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    reviews = []
    for item in soup.select(".business-review-view"):
        author_tag = item.select_one(".business-review-view__author-name")
        date_tag = item.select_one(".business-review-view__date")
        text_tag = item.select_one(".business-review-view__body")
        stars_tag = item.select_one(".business-rating-badge-view__stars")
        if not text_tag:
            continue
        text = text_tag.get_text(" ", strip=True)
        if len(text) < 10:
            continue
        author = author_tag.get_text(strip=True) if author_tag else None
        date = date_tag.get_text(strip=True) if date_tag else None
        rating = None
        if stars_tag:
            full = len(stars_tag.select("._full"))
            half = len(stars_tag.select("._half"))
            rating = full + half * 0.5
        reviews.append({
            "source": "yandex",
            "author": author,
            "date": date,
            "rating": rating,
            "text": text,
            "url": url,
        })
    return reviews


def parse_zoon():
    url = SOURCES["zoon"]["url"]
    html = _browse(url, wait_ms=4000)
    if not html:
        return []
    return _generic_from_html(html, "zoon", url)


def _generic_from_html(html, source_key, url):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    reviews = []
    for item in soup.find_all(attrs={"class": lambda x: x and ("review" in " ".join(x).lower() or "comment" in " ".join(x).lower())}):
        text_tag = item.select_one("[class*='text'], [class*='message'], [class*='content'], p")
        if not text_tag:
            ps = item.find_all("p")
            if ps:
                text_tag = ps[0]
        author_tag = item.select_one("[class*='author'], [class*='user'], [class*='name']")
        date_tag = item.select_one("time, [class*='date'], [class*='time']")
        if not text_tag:
            continue
        text = text_tag.get_text(" ", strip=True)
        if len(text) < 20:
            continue
        author = author_tag.get_text(strip=True) if author_tag else None
        date = date_tag.get("datetime") or date_tag.get_text(strip=True) if date_tag else None
        reviews.append({
            "source": source_key,
            "author": author,
            "date": date,
            "rating": None,
            "text": text,
            "url": url,
        })
    return reviews
