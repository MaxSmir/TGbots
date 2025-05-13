import requests
from bs4 import BeautifulSoup
from database import Postgres
import datetime


def get_page_content(url):
    response = requests.get(url)
    return response.content


def extract_news_titles(soup):
    return [title.get('href') for title in soup.find_all(class_='dfe7838f95 def3c4dc17 a334cd468c')]

def delete_news():
    connection = Postgres.open_connection()
    try:
        date_news = Postgres.get_date_news(connection)
        today_date = datetime.date.today()
        for date_add in date_news:
            delta = today_date - date_add[0]
            if delta.days >= 3:
                Postgres.delete_news(connection, date_add[0])
                print("Устаревшая новость удалена")
    finally:
        Postgres.close_connection(connection)


def extract_text_from_news_page(soup):
    result_text = ''

    try:
        result_text += soup.find('h1').text + '\n\n'
    except AttributeError:
        print("Error: Unable to find 'h1' tag.")
    try:
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            cleaned_text = p.text.strip()
            result_text += cleaned_text + '\n'
    except AttributeError:
        print("Error: Unable to find 'p' tags.")

    return result_text


def main():
    regions_mapping = {'16': 'Татарстан', '2': 'Башкортостан'}
    categories_mapping = {'society': 'Общество', 'incident': 'События', 'politics': 'Политика',
                          'economics': 'Экономика'}
    regions = ['16', '2']
    categories = ['society', 'incident', 'politics', 'economics']
    base_url = 'https://news.mail.ru/inregions/volgaregion/'
    delete_news()

    for region in regions:
        for category in categories:
            url = f'{base_url}{region}/{category}/'
            html_code = get_page_content(url)
            soup = BeautifulSoup(html_code, 'html.parser')
            response_titles = extract_news_titles(soup)

            for news_url in response_titles:
                connection = Postgres.open_connection()
                url_db = Postgres.get_url_news(connection)
                Postgres.close_connection(connection)

                if not url_db or news_url not in [url[0] for url in url_db]:
                    news_html_code = get_page_content(news_url)
                    news_soup = BeautifulSoup(news_html_code, 'html.parser')

                    result_text = extract_text_from_news_page(news_soup)
                    region_send = regions_mapping.get(region, '')
                    category_send = categories_mapping.get(category, '')
                    if region_send and category_send:
                        connection = Postgres.open_connection()
                        Postgres.add_news(connection, region_send, category_send, result_text + "\n" + news_url,
                                          news_url,
                                          datetime.date.today())
                        Postgres.close_connection(connection)
                        print(result_text)
                        print("\n\n")
                else:
                    print("Новость записана")


if __name__ == "__main__":
    main()
