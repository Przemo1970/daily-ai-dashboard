
import streamlit as st
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
from datetime import datetime, timedelta
import re
import json
import os

HISTORY_FILE = "history.json"

def clean_text(text):
    return re.sub(r'[^ -ąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s\w\.,:;?!@#&()"']+', '', text)

def safe_text(text):
    return text.encode("ascii", "ignore").decode()

def get_openai_news():
    url = "https://openai.com/blog"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    articles = soup.find_all('a', class_='group block')
    news = []
    for a in articles[:5]:
        title = a.find('h3')
        link = a['href']
        if title:
            news.append({
                "title": clean_text(title.text.strip()),
                "url": f"https://openai.com{link}"
            })
    return news

def get_producthunt_ai():
    url = "https://www.producthunt.com/topics/artificial-intelligence"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    scripts = soup.find_all('script')
    ai_projects = []
    for script in scripts:
        if '__NEXT_DATA__' in script.text:
            text = script.string
            if text:
                start = text.find('"products":')
                end = text.find('"topic"', start)
                raw = text[start:end]
                projects = raw.split('name":')
                for p in projects[1:6]:
                    name = p.split('"')[1]
                    ai_projects.append(clean_text(name))
            break
    return ai_projects

def save_to_history(openai_news, ph_projects):
    today = str(datetime.now().date())
    data = {
        "date": today,
        "openai": openai_news,
        "producthunt": ph_projects
    }
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = []

    history = [entry for entry in history if entry["date"] != today]
    history.append(data)

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_history(days=7):
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
    cutoff = datetime.now().date() - timedelta(days=days)
    return [entry for entry in history if datetime.strptime(entry["date"], "%Y-%m-%d").date() >= cutoff]

st.title("🧠 Daily AI Digest – z archiwum 7 dni")
st.write("Podsumowanie nowości z OpenAI i Product Hunt z ostatniego tygodnia.")

if st.button("🔄 Odśwież dane (dzisiaj)"):
    openai_news = get_openai_news()
    ph_projects = get_producthunt_ai()
    save_to_history(openai_news, ph_projects)
    st.success("Dane zaktualizowane i zapisane w historii!")

history = load_history()

for entry in sorted(history, key=lambda x: x['date'], reverse=True):
    st.subheader(f"📅 {entry['date']}")
    st.markdown("**OpenAI Blog:**")
    for item in entry["openai"]:
        st.markdown(f"- [{item['title']}]({item['url']})")
    st.markdown("**Product Hunt (AI Projects):**")
    for name in entry["producthunt"]:
        st.markdown(f"- {name}")
