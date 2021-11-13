import os
import json
import pathlib
import logging
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def parse_book_page(soup, books_folder, images_folder, filename):
    comments_selector = '.texts .black'
    comments = soup.select(comments_selector)

    genres_selector = 'span.d_book a'
    links_genre = soup.select(genres_selector)

    title_with_author_selector = 'body h1'
    title_with_author = soup.select_one(title_with_author_selector)
    title, author = title_with_author.text.split('::')

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
        'comments': [tag.text for tag in comments],
    }
    return parsed_book


def download_txt(parsed_book, image_id):
    book_id, _ = os.path.splitext(image_id)
    book_id = {'id': book_id}
    download_url = 'https://tululu.org/txt.php'
    download_url_response = requests.get(download_url, params=book_id)
    check_for_redirect(download_url_response)
    response.raise_for_status()

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


def download_description_book(parsed_book):
    with open('parsed_book.json', 'w', encoding='utf8') as description_book:
        json.dump(parsed_book, description_book, ensure_ascii=False)


def download_books(soup, basic_url, books_folder, images_folder):
    relative_images_urls_selector = '.bookimage a img'
    relative_images_urls = soup.select(relative_images_urls_selector)
    for relative_image_url in relative_images_urls:
        relative_image_url = relative_image_url['src']

        parse_image_url = urlsplit(relative_image_url)
        image_id = os.path.split(parse_image_url.path)[-1]
        filename = unquote(image_id)

        parsed_book = parse_book_page(
            soup, books_folder,
            images_folder, filename
        )

        download_txt(parsed_book, image_id)
        download_image(basic_url, parsed_book, relative_image_url)
        download_description_book(parsed_book)


for book in range(0, 2):
    books_folder = 'books'
    images_folder = 'images'
    url = f'https://tululu.org/l55/{book}/'
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')
    selector = '.bookimage a'
    books = soup.select(selector)

    for book in books:
        try:
            id = book['href']
            basic_url = urljoin(url, id)
            response = requests.get(basic_url)
            check_for_redirect(response)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')

            download_books(
                soup, basic_url,
                books_folder, images_folder
            )
        except:
            logging.basicConfig(level=logging.DEBUG)
