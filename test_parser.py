from parser.things1000 import parse_1000things_wien

if __name__ == "__main__":
    news = parse_1000things_wien()
    for i, item in enumerate(news, 1):
        print(f"{i}. {item['title']} - {item['link']}")
