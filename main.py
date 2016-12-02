import os
import shutil
import time
import json

import requests
from jinja2 import Environment, FileSystemLoader

from goodreadsapi import get_book_details_by_name, BookNotFound

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, 'dist')
IMAGES_DIR = os.path.join(DIST_DIR, 'images')
SOURCE_FILE = os.path.join(BASE_DIR, 'source.txt')
TEMPLATE_FILE = 'template.html'
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False, loader=FileSystemLoader(BASE_DIR), trim_blocks=False)


def create_images_dir():
    os.makedirs(IMAGES_DIR, exist_ok=True)


def check_image_exists(file_name):
    return os.path.isfile(os.path.join(IMAGES_DIR, file_name))


def download_image(image_url, image_name):
    if check_image_exists(file_name=image_name):
        return
    image_path = os.path.join(IMAGES_DIR, image_name)
    r = requests.get(image_url, stream=True)
    if r.status_code == 200:
        with open(image_path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)


def get_book_data(source_file=SOURCE_FILE):
    books = []
    with open(source_file) as f:
        for line in f.readlines():
            name, author, votes, suggested_by = [x.strip()
                                                 for x in line.split('|')]
            book = {
                'name': name,
                'author': author,
                'votes': int(votes),
                'suggested_by': suggested_by
            }
            books.append(book)
    return books


def get_goodreads_data(books):
    books = books[:10]
    for book in books:
        search_term = "{} {}".format(book['name'], book['author'])
        try:
            book_goodreads = get_book_details_by_name(book_name=search_term)
        except BookNotFound:
            continue
        keys = ['image_url', 'publication_year', 'num_pages', 'average_rating',
                'ratings_count', 'url', 'goodreads_id']
        for key in keys:
            book[key] = book_goodreads[key]
        time.sleep(1)
    return books


def download_book_covers(books):
    for book in books:
        image_url = book['image_url']
        extention = image_url.split('.')[-1]
        image_name = "{}.{}".format(book['goodreads_id'], extention)
        download_image(image_url=image_url, image_name=image_name)
        book['image_name'] = image_name
        time.sleep(1)
    return books


def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def write_output(books):
    output = os.path.join(DIST_DIR, 'index.html')
    html = render_template(TEMPLATE_FILE, context={'books': books})
    with open(output, 'w') as f:
        f.write(html)


def main():
    books = get_book_data()
    books = get_goodreads_data(books=books)
    books = download_book_covers(books=books)
    write_output(books=books)

    with open('output.json', 'w') as f:
        json.dump(obj=books, fp=f, indent=2)


if __name__ == '__main__':
    create_images_dir()
    main()
