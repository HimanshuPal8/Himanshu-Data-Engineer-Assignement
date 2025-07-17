import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DB_PATH = 'articles.db'
SKIFT_URL = 'https://skift.com/news/'
PHOCUSWIRE_URL = 'https://www.phocuswire.com/'

def initialize_database():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            article_id TEXT PRIMARY KEY,
            url TEXT,
            title TEXT,
            published_at TEXT,
            source TEXT
        )
    """)
    return connection

def create_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def parse_date(date_str):
    formats = ['%b %d, %Y', '%B %d, %Y', '%Y-%m-%dT%H:%M:%S%z']
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {date_str}")

def scrape_skift(session):
    try:
        response = session.get(SKIFT_URL, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[Error] Failed to fetch Skift: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.select('article.post')

    for article in articles:
        try:
            anchor = article.find('a', href=True)
            date_tag = article.find('time')

            if not anchor or not date_tag:
                continue

            url = anchor['href']
            title = anchor.get_text(strip=True)
            published = parse_date(date_tag.get_text()).isoformat()
            article_id = url.split('/')[-1]

            yield (article_id, url, title, published, 'skift')
        except Exception as e:
            print(f"[Warning] Skipped Skift article: {e}")

def scrape_phocuswire(session):
    try:
        response = session.get(PHOCUSWIRE_URL, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[Error] Failed to fetch PhocusWire: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.select('article')

    for article in articles:
        try:
            anchor = article.find('a', href=True)
            date_tag = article.find('time')

            if not anchor or not date_tag:
                continue

            href = anchor['href']
            url = href if href.startswith('http') else PHOCUSWIRE_URL.rstrip('/') + href
            title = anchor.get_text(strip=True)
            published = parse_date(date_tag.get_text()).isoformat()
            article_id = url.split('/')[-1]

            yield (article_id, url, title, published, 'phocuswire')
        except Exception as e:
            print(f"[Warning] Skipped PhocusWire article: {e}")

def run_pipeline():
    session = create_session()
    conn = initialize_database()
    cursor = conn.cursor()
    new_articles = 0

    scrapers = [scrape_skift, scrape_phocuswire]

    for scraper in scrapers:
        for article_id, url, title, published_at, source in scraper(session):
            try:
                cursor.execute("""
                    INSERT INTO articles (article_id, url, title, published_at, source)
                    VALUES (?, ?, ?, ?, ?)
                """, (article_id, url, title, published_at, source))
                new_articles += 1
            except sqlite3.IntegrityError:
                continue

    conn.commit()
    print(f"✅ {new_articles} new articles inserted.\n")
    print("📰 Latest 5 Articles:\n")

    cursor.execute("""
        SELECT title, url, source, published_at
        FROM articles
        ORDER BY published_at DESC
        LIMIT 5
    """)
    rows = cursor.fetchall()

    for title, url, source, published in rows:
        print(f"- [{source.upper()}] {title} ({published})\n  {url}\n")

    conn.close()

if __name__ == "__main__":
    run_pipeline()
