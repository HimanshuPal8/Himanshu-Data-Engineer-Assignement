# News Article Pipeline — Unravel Data Engineer Assignment

This Python-based pipeline extracts the latest articles from **Skift** and **PhocusWire**, stores them in a local **SQLite** database, and prints the **top 5 most recent articles** on every run.

---

## 🔍 Features

- ✅ **Web scraping** from real news sites (no public APIs available)
- ✅ **Incremental loading**: only new articles inserted (via `article_id` uniqueness)
- ✅ **SQLite** schema with timestamps, source, and deduplication
- ✅ **Robust error handling** with retry logic and fallbacks
- ✅ **Readable and modular code** with detailed inline comments
- ✅ **Unit tests** for key functionality

---

## 📁 Schema Design

The `articles` table is defined as:

| Column        | Type   | Description                         |
|---------------|--------|-------------------------------------|
| article_id    | TEXT   | Unique identifier (from URL slug)   |
| url           | TEXT   | Full article URL                    |
| title         | TEXT   | Article headline                    |
| published_at  | TEXT   | ISO-formatted publication timestamp |
| source        | TEXT   | "skift" or "phocuswire"             |

## 🚀 How to Run

1. **Install dependencies**

-> pip install requests beautifulsoup4

2. **To run code**

-> python pipeline.py




