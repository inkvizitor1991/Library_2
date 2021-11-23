import argparse
import json
import logging
import os
import pathlib
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def parse_book_page(soup, books_path, images_path, filename):
    comments_selector = '.texts .black'
    comments = soup.select(comments_selector)

    genres_selector = 'span.d_book a'
    links_genre = soup.select(genres_selector)

    title_with_author_selector = 'body h1'
    title_with_author = soup.select_one(title_with_author_selector)
    title, author = title_with_author.text.split('::')

    pathlib.Path(books_path).mkdir(parents=True, exist_ok=True)
    pathlib.Path(images_path).mkdir(parents=True, exist_ok=True)
    img_scr = os.path.join(images_path, f'{filename}')
    book_path = os.path.join(books_path, f'{title.strip()}.txt')

    parsed_book = {
        'title': title.strip(),
        'autor': author.strip(),
        'img_scr': img_scr,
        'genres': [tag.text for tag in links_genre],
        'book_path': book_path,
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


def download_description_book(parsed_book, json_path):
    with open(json_path, 'w', encoding='utf8') as description_book:
        json.dump(parsed_book, description_book, ensure_ascii=False)


def download_books(soup, basic_url, books_path, images_path, skip_imgs,
                   skip_txt, json_path):
    relative_images_urls_selector = '.bookimage a img'
    relative_images_urls = soup.select(relative_images_urls_selector)
    for relative_image_url in relative_images_urls:
        relative_image_url = relative_image_url['src']

        parse_image_url = urlsplit(relative_image_url)
        image_id = os.path.split(parse_image_url.path)[-1]
        filename = unquote(image_id)

        parsed_book = parse_book_page(
            soup, books_path,
            images_path, filename
        )
        if skip_txt:
            download_txt(parsed_book, image_id)
        if skip_imgs:
            download_image(basic_url, parsed_book, relative_image_url)
        download_description_book(parsed_book, json_path)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--start_page', nargs='?',
        type=int, default=0,
        help='С какой страницы скачать'
    )
    parser.add_argument(
        '--end_page', nargs='?',
        type=int, default=0,
        help='С какой по какую страницы скачать'
    )
    parser.add_argument(
        '--dest_folder',
        help='Путь к каталогу с результатами парсинга: картинкам, книгам, JSON.',
        default=os.path.abspath(os.curdir)
    )
    parser.add_argument(
        '--skip_txt',
        action='store_false',
        help='Не скачивать книги.'
    )
    parser.add_argument(
        '--skip_imgs',
        action='store_false',
        help='Не скачивать картинки.'
    )
    parser.add_argument(
        '--json_path',
        help='Указать свой путь к *.json файлу с результатами.',
        default='parsed_book.json'
    )
    return parser


if __name__ == '__main__':
    books_folder = 'books'
    images_folder = 'images'

    parser = get_parser()
    args = parser.parse_args()
    skip_txt = args.skip_txt
    skip_imgs = args.skip_imgs
    start_page = args.start_page
    end_page = args.end_page
    dest_folder = args.dest_folder

    if end_page == 0:
        end_page = start_page + 1
    else:
        end_page += 1

    books_path = Path(dest_folder, books_folder)
    images_path = Path(dest_folder, images_folder)
    json_path = Path(dest_folder, args.json_path)

    for book in range(start_page, end_page):
        url = f'https://tululu.org/l55/{book}/'
        response = requests.get(url)
        check_for_redirect(response)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        selector = '.bookimage a'
        books = soup.select(selector)

        for book in books:
            try:
                book_id = book['href']
                basic_url = urljoin(url, book_id)
                response = requests.get(basic_url)
                check_for_redirect(response)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'lxml')

                download_books(
                    soup, basic_url,
                    books_path, images_path,
                    skip_imgs, skip_txt,
                    json_path
                )
            except:
                logging.basicConfig(level=logging.DEBUG)