
import streamlit as st
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
from datetime import datetime

# --- FUNKCJE ---

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
                "title": title.text.strip(),
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
                    ai_projects.append(name)
            break
    return ai_projects

def generate_pdf(openai_news, ph_projects):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Daily AI Digest", ln=True, align='C')
    pdf.cell(200, 10, txt=str(datetime.now().date()), ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(200, 10, txt="🧠 OpenAI Blog", ln=True)
    pdf.set_font("Arial", size=11)
    for item in openai_news:
        pdf.multi_cell(0, 10, f"- {item['title']} ({item['url']})")

    pdf.ln(5)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(200, 10, txt="🚀 Product Hunt – AI Projects", ln=True)
    pdf.set_font("Arial", size=11)
    for name in ph_projects:
        pdf.cell(200, 10, f"- {name}", ln=True)

    path = "/tmp/ai_digest.pdf"
    pdf.output(path)
    return path

# --- INTERFEJS ---

st.title("🧠 Daily AI Digest")
st.write("Automatyczne podsumowanie nowości z OpenAI i Product Hunt")

if st.button("🔄 Odśwież dane"):
    openai_news = get_openai_news()
    ph_projects = get_producthunt_ai()
    st.success("Dane zostały zaktualizowane.")
else:
    openai_news = get_openai_news()
    ph_projects = get_producthunt_ai()

st.subheader("🧠 OpenAI Blog")
for news in openai_news:
    st.markdown(f"- [{news['title']}]({news['url']})")

st.subheader("🚀 Top AI projekty z Product Hunt")
for name in ph_projects:
    st.markdown(f"- {name}")

pdf_path = generate_pdf(openai_news, ph_projects)
with open(pdf_path, "rb") as f:
    st.download_button("📄 Pobierz PDF", f, file_name="daily_ai_digest.pdf")
