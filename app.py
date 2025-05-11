import streamlit as st
import requests
from datetime import datetime, timedelta
import feedparser
import re

st.set_page_config(page_title="Daily AI Digest", layout="wide")

# === Konfiguracja ===
DAYS_BACK = 7
KEYWORDS = ["openai", "chatgpt", "gpt", "ai", "announcement", "launch", "product", "update"]

# === Funkcje pomocnicze ===
def clean_text(text):
    return re.sub(r'[^ -~ąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s\w\.,:;?!@#&()"’‘]+', '', text)

def fetch_rss_entries():
    feeds = [
        ("OpenAI Blog", "https://openai.com/blog/rss.xml"),
        ("Product Hunt Launches", "https://www.producthunt.com/feed")
    ]
    entries = []
    for source_name, feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                entries.append({
                    "source": source_name,
                    "title": entry.get("title", "No title"),
                    "summary": entry.get("summary", "No summary"),
                    "date": entry.get("published", entry.get("updated", datetime.utcnow().isoformat())),
                    "url": entry.get("link", "#")
                })
        except Exception as e:
            print(f"Błąd pobierania z {feed_url}: {e}")
    print(f"Wczytano {len(entries)} wpisów ze wszystkich źródeł")
    return entries

def parse_date(date_str):
    try:
        parsed = feedparser._parse_date(date_str)
        if parsed:
            return datetime(*parsed[:6])
        else:
            return datetime.utcnow()
    except:
        return datetime.utcnow()

def filter_entries(entries, keywords, days):
    today = datetime.utcnow()
    threshold = today - timedelta(days=days)
    results = []

    for entry in entries:
        try:
            date = parse_date(entry["date"])
            text = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
            if date >= threshold and any(kw in text for kw in keywords):
                entry["date"] = date.strftime("%Y-%m-%d")
                results.append(entry)
        except Exception as e:
            print(f"Błąd przy analizie wpisu: {e}")
            continue

    print(f"Po filtrze pozostało {len(results)} wpisów")
    return results

# === Dane ===
data = fetch_rss_entries()
filtered_data = filter_entries(data, KEYWORDS, DAYS_BACK)

# === UI ===
st.title("\U0001F4C8 Daily AI Digest – Archiwum 7 dni")
if not filtered_data:
    st.info("Brak nowych wpisów z ostatnich 7 dni.")
else:
    for entry in filtered_data:
        st.markdown(f"### [{clean_text(entry['title'])}]({entry['url']})")
        st.markdown(f"**Źródło:** {entry['source']}  ")
        st.markdown(f"**Data:** {entry['date']}  ")
        st.markdown(clean_text(entry['summary']))
        st.markdown("---")
