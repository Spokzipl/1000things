import psycopg2
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import openai

openai.api_key = "YOUR_OPENAI_API_KEY"
DATABASE_URL = "YOUR_RAILWAY_POSTGRES_URL"

def parse_1000things_wien():
    # (оставляем код парсера без изменений)
    pass

def translate_title(title):
    # (оставляем код перевода без изменений)
    pass

def main():
    conn = psycopg2.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS articles (
        id SERIAL PRIMARY KEY,
        title_de TEXT,
        title_ru TEXT,
        link TEXT UNIQUE,
        date_added TIMESTAMP
    )''')
    conn.commit()

    articles = parse_1000things_wien()

    for article in articles:
        link = article['link']
        title_de = article['title']
        c.execute("SELECT id FROM articles WHERE link = %s", (link,))
        if c.fetchone():
            continue
        title_ru = translate_title(title_de)
        c.execute("INSERT INTO articles (title_de, title_ru, link, date_added) VALUES (%s, %s, %s, %s)",
                  (title_de, title_ru, link, datetime.now()))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
