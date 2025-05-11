import streamlit as st
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
from datetime import datetime
import re

def clean_text(text):
    return re.sub(r'[^\x00-\x7FąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s\w\.,:;?!@#&()"\']+', '', text)

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

def generate_pdf(_

