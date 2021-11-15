# Парсер книг с сайта [tululu.org](https://tululu.org)

1. Скачивает книги в жанре фантастика.
2. Для каждой книги скачивается обложка.
3. Сохраняет в словарь описание каждой книги со следующим содержанием:

* Название
* Имя автора
* Жанр
* Комментарии
* Путь до обложки
* Путь до книги

### Как установить

Для запуска вам потребуется:

1. Свежая версия [Python](https://www.python.org).
2. Наличие следующих библиотек:

```
$ pip install urllib3 requests BeautifulSoup4 lxml
```

### Аргументы

Доступны следующие аргументы:

* --dest_folder — путь к каталогу с результатами парсинга: картинкам, книгам,
  JSON.
* --skip_imgs — не скачивать картинки.
* --skip_txt — не скачивать книги.
* --json_path — указать свой путь к *.json файлу с результатами.
* --start_page – какую страницу скачать.
* --start_page --end_page – по какую страницу скачать.

Примеры запуска скрипта:
```
$ python library.py --start_page 1 --end_page 2
$ python library.py --start_page 1
$ python library.py --start_page 1 --dest_folder
$ python library.py --start_page 1 --skip_txt
$ python library.py --start_page 1 --skip_imgs
$ python library.py --start_page 1 --json_path parsed_book.json
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для
веб-разработчиков [dvmn.org](https://dvmn.org/).