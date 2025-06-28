import psycopg2
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

def parse_1000things_wien():
    url = "https://www.1000thingsmagazine.com/de/at/wien/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    news_items = []

    articles = soup.select("article[post-id]")

    print(f"[parse_1000things_wien] Найдено статей: {len(articles)}")

    for article in articles:
        title_tag = article.select_one("h2.card__title a")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        link = title_tag.get("href")
        if link and not link.startswith("http"):
            link = "https://www.1000thingsmagazine.com" + link

        news_items.append({
            "title": title,
            "link": link
        })

    return news_items

def translate_title(title):
    print(f"[translate_title] Переводим: {title}")
    return title + " [RU]"

def main():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("[main] Ошибка: DATABASE_URL не задана в переменных окружения!")
        return

    try:
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
                print(f"[main] Статья уже в базе: {link}")
                continue

            title_ru = translate_title(title_de)
            c.execute(
                "INSERT INTO articles (title_de, title_ru, link, date_added) VALUES (%s, %s, %s, %s)",
                (title_de, title_ru, link, datetime.now())
            )
            print(f"[main] Добавлена статья: {title_de}")

        conn.commit()
    except Exception as e:
        print(f"[main] Ошибка: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
            print("[main] Соединение с базой закрыто.")

if __name__ == "__main__":
    main()
