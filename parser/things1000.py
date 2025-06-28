import psycopg2
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

def parse_1000things_wien():
    url = "https://www.1000things.at/wien/"  # пример адреса
    print(f"[parse_1000things_wien] Парсим: {url}")
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    # Подбери правильные селекторы под сайт 1000things
    article_tags = soup.select("article")  # пример, надо адаптировать
    
    print(f"[parse_1000things_wien] Найдено статей: {len(article_tags)}")

    for article in article_tags:
        title_tag = article.select_one("h2 a")  # пример заголовка с ссылкой
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        link = title_tag.get("href")
        if link and not link.startswith("http"):
            link = "https://www.1000things.at" + link
        articles.append({"title": title, "link": link})

    print(f"[parse_1000things_wien] Собрано статей: {len(articles)}")
    return articles

def translate_title(title):
    print(f"[translate_title] Переводим: {title}")
    # Заглушка, можно заменить на вызов OpenAI
    return title + " [RU]"

def main():
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
