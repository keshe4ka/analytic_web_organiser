import re
import ratelim
import requests
from requests_html import HTMLSession
from requests import exceptions
from bs4 import BeautifulSoup
from time import sleep

# habr_url = 'https://habr.com/ru/post/'
habr_url = 'https://habr.com/ru/post/596491/'
count_of_posts = 100000


@ratelim.patient(1, 1)
def get_data_from_post(post_id):
    url = habr_url + str(post_id)

    try:
        response = requests.get(url)
        response.raise_for_status()
        title, text, habs, tags, rating, bookmarks, comments, user, date = get_elements(response)
        data = [title, text, habs, tags, rating, bookmarks, comments, user, date]

        return data
    except requests.exceptions.HTTPError as ex:
        pass


def get_elements(response):
    soup = BeautifulSoup(response.content, 'html.parser')

    # Заголовок
    title = soup.find('meta', property='og:title')
    title = str(title).split('="')[1].split('" ')[0]

    # Текст
    text = str(soup.find('div', id="post-content-body"))
    text = re.sub(r'\<[^>]*\>', '', text)
    text = re.sub('\n', ' ', text)

    # Хабы
    habs = str(soup.findAll('a', class_="tm-hubs-list__link"))
    habs = re.sub(r'\<[^>]*\>', '', habs)
    habs = re.sub('\s+', ' ', habs)
    habs = habs.split(',')
    for i in range(len(habs)):
        habs[i] = re.sub(r'\[|\]', '', habs[i])
        habs[i] = habs[i].strip()
        habs[i] = habs[i].lower()

    # Теги
    tags = str(soup.findAll('a', class_="tm-tags-list__link"))
    tags = re.sub(r'\<[^>]*\>', '', tags)
    tags = re.sub('\s+', ' ', tags)
    tags = tags.split(',')
    for i in range(len(tags)):
        tags[i] = re.sub(r'\[|\]', '', tags[i])
        tags[i] = tags[i].strip()
        tags[i] = tags[i].lower()

    # Рейтинг
    rating = str(soup.find('span',
                           class_='tm-votes-meter__value tm-votes-meter__value_positive tm-votes-meter__value_appearance-article tm-votes-meter__value_rating'))
    rating = int(re.sub(r'\<[^>]*\>', '', rating))

    # Кол-во сохранений
    bookmarks = str(soup.find('span', class_='bookmarks-button__counter'))
    bookmarks = int(re.sub(r'\<[^>]*\>', '', bookmarks))

    # Кол-во комментариев
    comments = str(soup.find('span',
                             class_='tm-article-comments-counter-link__value tm-article-comments-counter-link__value_contrasted'))
    comments = re.sub(r'\<[^>]*\>', '', comments)
    comments = int(re.sub(r'\D', '', comments))

    # Автор
    user = str(soup.find('span', class_='tm-user-info__user'))
    user = re.sub(r'\<[^>]*\>', '', user)
    user = re.sub(r'\s', '', user)

    # Дата публикации
    date = str(soup.find('span', class_='tm-article-snippet__datetime-published'))
    date = re.sub(r'\<[^>]*\>', '', date)

    return title, text, habs, tags, rating, bookmarks, comments, user, date


if __name__ == '__main__':
    get_data_from_post()
