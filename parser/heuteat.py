import requests
from bs4 import BeautifulSoup

def parse_heuteat():
    url = "https://www.heute.at"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    news_items = []

    articles = soup.select("div.article-teaser")
    print(f"Найдено элементов: {len(articles)}")  # добавь это

    for article in articles:
        title_tag = article.select_one("a.headline")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        link = title_tag.get("href")
        if link and not link.startswith("http"):
            link = url + link
        news_items.append({"title": title, "link": link})

    return news_items
