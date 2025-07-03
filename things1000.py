import os
import time
import requests
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

def parse_1000things_wien():
    url = "https://www.1000thingsmagazine.com/de/at/wien/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    print(f"[parse_1000things_wien] Парсим: {url}")
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.select("article[post-id]")

    print(f"[parse_1000things_wien] Найдено статей: {len(articles)}")
    news_items = []

    for i, article in enumerate(articles, 1):
        link_tag = article.select_one("a h3")
        if not link_tag:
            print(f"Статья #{i}: Заголовок не найден")
            continue

        a_tag = link_tag.find_parent("a")
        if not a_tag:
            print(f"Статья #{i}: Ссылка не найдена")
            continue

        title = ''.join(link_tag.stripped_strings)
        link = a_tag.get("href")
        if link and not link.startswith("http"):
            link = "https://www.1000thingsmagazine.com" + link

        news_items.append({
            "title": title,
            "link": link
        })

    print(f"[parse_1000things_wien] Собрано статей: {len(news_items)}")
    return news_items


def translate_title(title):
    print(f"[translate_title] Переводим: {title}")
    return title + " [RU]"  # Место для интеграции с переводчиком


def should_run_script(cursor):
    cursor.execute("""
        SELECT enabled FROM settings
        WHERE name = '1000things' AND city = 'Vienna'
        LIMIT 1
    """)
    row = cursor.fetchone()
    return row and row[0] is True


def ensure_articles_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles_vienna (
            id SERIAL PRIMARY KEY,
            title_de TEXT,
            title_ru TEXT,
            link TEXT UNIQUE NOT NULL,
            date_added TIMESTAMP
        )
    ''')


def run_parser_once():
    if not DATABASE_URL:
        print("[run_parser_once] Ошибка: DATABASE_URL не задана в переменных окружения!")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_client_encoding('UTF8')
        c = conn.cursor()

        # Проверяем флаг активности в таблице settings
        if not should_run_script(c):
            print("[run_parser_once] Парсинг отключён через settings (enabled = false)")
            return

        ensure_articles_table(c)
        conn.commit()

        articles = parse_1000things_wien()

        for article in articles:
            link = article['link']
            title_de = article['title']

            c.execute("SELECT id FROM articles_vienna WHERE link = %s", (link,))
            if c.fetchone():
                print(f"[run_parser_once] Статья уже в базе: {link}")
                continue

            title_ru = translate_title(title_de)
            c.execute("""
                INSERT INTO articles_vienna (title_de, title_ru, link, date_added)
                VALUES (%s, %s, %s, %s)
            """, (title_de, title_ru, link, datetime.now()))
            print(f"[run_parser_once] Добавлена статья: {title_de}")

        conn.commit()

    except Exception as e:
        print(f"[run_parser_once] Ошибка: {e}")
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    while True:
        print("\n[main] Запуск парсера...")
        run_parser_once()
        print("[main] Ожидание 1 час...\n")
        time.sleep(3600)  # Засыпаем на 1 час
