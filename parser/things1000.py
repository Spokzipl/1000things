import psycopg2
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

def parse_1000things_wien():
    print("[parse_1000things_wien] Начинаем парсинг...")
    # Здесь должен быть код парсера, например:
    # Для демонстрации вернём фиктивный список статей
    articles = [
        {"title": "Beispiel Titel 1", "link": "http://example.com/1"},
        {"title": "Beispiel Titel 2", "link": "http://example.com/2"},
    ]
    print(f"[parse_1000things_wien] Найдено статей: {len(articles)}")
    return articles

def translate_title(title):
    print(f"[translate_title] Переводим: {title}")
    # Здесь должен быть реальный код перевода
    # Для теста просто вернём заголовок с приставкой "[RU]"
    return title + " [RU]"

def main():
    print(f"[main] DATABASE_URL = {DATABASE_URL}")
    if not DATABASE_URL:
        print("[main] Ошибка: DATABASE_URL не задана в переменных окружения!")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()
        print("[main] Создаём таблицу articles, если её нет...")
        c.execute('''CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title_de TEXT,
            title_ru TEXT,
            link TEXT UNIQUE,
            date_added TIMESTAMP
        )''')
        conn.commit()
        print("[main] Таблица создана или уже существует.")

        articles = parse_1000things_wien()

        for article in articles:
            link = article['link']
            title_de = article['title']
            c.execute("SELECT id FROM articles WHERE link = %s", (link,))
            if c.fetchone():
                print(f"[main] Статья с ссылкой {link} уже есть в базе, пропускаем.")
                continue
            title_ru = translate_title(title_de)
            c.execute(
                "INSERT INTO articles (title_de, title_ru, link, date_added) VALUES (%s, %s, %s, %s)",
                (title_de, title_ru, link, datetime.now())
            )
            print(f"[main] Добавлена статья: {title_de}")
        conn.commit()
        print("[main] Все изменения зафиксированы в базе.")
    except Exception as e:
        print(f"[main] Ошибка при работе с базой данных: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
            print("[main] Соединение с базой закрыто.")

if __name__ == "__main__":
    main()
