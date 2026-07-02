import os
import sqlite3
from datetime import datetime


def init_db(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reviews.db")
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            author TEXT,
            date TEXT,
            rating REAL,
            text TEXT NOT NULL,
            url TEXT,
            fetched_at TEXT NOT NULL,
            is_new INTEGER DEFAULT 1
        )
        """
    )
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_reviews_source ON reviews(source)
        """
    )
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_reviews_date ON reviews(date)
        """
    )
    conn.commit()
    return conn


def insert_review(conn, source, author, date, rating, text, url):
    if not text or not text.strip():
        return None
    normalized = text.strip()
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM reviews WHERE source = ? AND text = ?",
        (source, normalized),
    )
    if cur.fetchone():
        return None
    cur.execute(
        """
        INSERT INTO reviews (source, author, date, rating, text, url, fetched_at, is_new)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (source, author or "Аноним", date or datetime.now().isoformat(), rating, normalized, url, datetime.now().isoformat()),
    )
    conn.commit()
    return cur.lastrowid


def get_reviews(conn, source=None, limit=None):
    cur = conn.cursor()
    query = "SELECT * FROM reviews WHERE 1=1"
    params = []
    if source:
        query += " AND source = ?"
        params.append(source)
    query += " ORDER BY fetched_at DESC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    cur.execute(query, params)
    return cur.fetchall()


def get_stats(conn):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT source, COUNT(*), AVG(rating)
        FROM reviews
        GROUP BY source
        ORDER BY COUNT(*) DESC
        """
    )
    return cur.fetchall()


def mark_all_seen(conn):
    cur = conn.cursor()
    cur.execute("UPDATE reviews SET is_new = 0 WHERE is_new = 1")
    conn.commit()


def get_new_reviews(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM reviews WHERE is_new = 1 ORDER BY fetched_at DESC")
    return cur.fetchall()
