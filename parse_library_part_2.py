import os
import pathlib
import logging
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def parse_book_page(soup, image_id):
    comments = soup.find_all('div', class_='texts')
    links_genre = soup.find('span', class_='d_book').find_all('a')
    title, author = soup.find('body').find('h1').text.split('::')
    filename = unquote(image_id)

    pathlib.Path(books_folder).mkdir(parents=True, exist_ok=True)
    pathlib.Path(images_folder).mkdir(parents=True, exist_ok=True)
    filepath_images = os.path.join(images_folder, f'{filename}')
    filepath_books = os.path.join(books_folder, f'{title.strip()}.txt')

    parsed_book = {
        'title': title.strip(),
        'autor': author.strip(),
        'img_scr': filepath_images,
        'genres': [tag.text for tag in links_genre],
        'book_path': filepath_books,
        'comments': [tag.find(class_='black').contents for tag in comments],
    }
    return parsed_book


def download_txt(parsed_book, download_url_response):
    filepath = parsed_book['book_path']
    with open(f'{filepath}', 'w') as file:
        file.write(download_url_response.text)


def download_image(basic_url, parsed_book, relative_image_url):
    image_url = parsed_book['img_scr']
    basic_image_url = urljoin(basic_url, relative_image_url)
    response = requests.get(basic_image_url)
    response.raise_for_status()

    with open(f'{image_url}', 'wb') as file:
        file.write(response.content)


for book in range(0, 11):
    books_folder = 'books'
    images_folder = 'images'
    url = f'https://tululu.org/l55/{book}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    cards = soup.find_all('div', class_="bookimage")

    for card in cards:
        try:
            id = card.find('a')['href']
            basic_url = urljoin(url, id)
            response = requests.get(basic_url)
            check_for_redirect(response)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')

            relative_image_url = \
                soup.find(class_='bookimage').find('a').find('img')['src']

            parse_image_url = urlsplit(url)
            image_id = os.path.split(parse_image_url.path)[-1]
            id, _ = os.path.splitext(image_id)

            book_id = {'id': id}
            download_url = 'https://tululu.org/txt.php'
            download_url_response = requests.get(download_url, params=book_id)
            check_for_redirect(download_url_response)
            response.raise_for_status()

            parsed_book = parse_book_page(soup, parse_image_url)
            download_txt(parsed_book, download_url_response)
            download_image(basic_url, parsed_book, relative_image_url)
        except:
            logging.basicConfig(level=logging.DEBUG)
