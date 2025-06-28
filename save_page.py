import requests

url = "https://www.1000thingsmagazine.com/de/at/wien/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
response.raise_for_status()

with open("page.html", "w", encoding="utf-8") as file:
    file.write(response.text)

print("HTML страницы сохранён в page.html")