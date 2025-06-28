import os
import psycopg2
from datetime import datetime
from parser.things1000 import parse_1000things_wien

DATABASE_URL = os.getenv("DATABASE_URL")

def translate_title(title):
    return title + " [RU]"

def process_articles():
    if not DATABASE_URL:
        print("DATABASE_URL не задана в окружении!")
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
        print(f"Найдено статей: {len(articles)}")

        for article in articles:
            link = article['link']
            title_de = article['title']

            c.execute("SELECT id FROM articles WHERE link = %s", (link,))
            if c.fetchone():
                print(f"Статья с ссылкой {link} уже есть в базе, пропускаем.")
                continue

            title_ru = translate_title(title_de)

            c.execute(
                "INSERT INTO articles (title_de, title_ru, link, date_added) VALUES (%s, %s, %s, %s)",
                (title_de, title_ru, link, datetime.now())
            )
            print(f"Добавлена статья: {title_de}")

        conn.commit()
        print("Все изменения зафиксированы в базе.")

    except Exception as e:
        print(f"Ошибка при работе с базой данных: {e}")

    finally:
        if 'conn' in locals():
            conn.close()
            print("Соединение с базой закрыто.")

if __name__ == "__main__":
    process_articles()
