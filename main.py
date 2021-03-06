import os
import time
import json
import logging
import logging.handlers

from jinja2 import Environment, FileSystemLoader

from goodreadsapi import get_book_details_by_name, BookNotFound
from utils import download_image
from settings import (BASE_DIR, IMAGES_DIR, SOURCE_FILE,
                      LOG_FILENAME, OUTPUT_FILE)

TEMPLATE_FILE = 'template.html'
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False, loader=FileSystemLoader(BASE_DIR), trim_blocks=False)
my_logger = logging.getLogger('MyLogger')


def set_logger():
    my_logger = logging.getLogger('MyLogger')
    my_logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                                   maxBytes=20000000,
                                                   backupCount=50,
                                                   )
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    my_logger.addHandler(handler)


def create_images_dir():
    os.makedirs(IMAGES_DIR, exist_ok=True)


def get_book_data(source_file=SOURCE_FILE):
    my_logger.debug('Reading from source file')
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
    my_logger.debug('Reading from source file complete')
    my_logger.debug("Total books: {}".format(len(books)))
    return books


def get_goodreads_data(books):
    goodread_books = []
    for book in books:
        search_term = "{} {}".format(book['name'], book['author'])
        my_logger.debug("Fetching book details for: {}".format(search_term))
        try:
            book_goodreads = get_book_details_by_name(book_name=search_term)
        except BookNotFound:
            my_logger.debug("Book not found: {}".format(search_term))
            continue
        keys = ['image_url', 'publication_year', 'num_pages', 'average_rating',
                'ratings_count', 'url', 'goodreads_id']
        for key in keys:
            book[key] = book_goodreads[key]
        goodread_books.append(book)
        time.sleep(1)
    my_logger.debug('Fetching book details from Goodreads is complete')
    my_logger.debug("Total books fetched: {}".format(len(goodread_books)))
    return goodread_books


def download_book_covers(books):
    for book in books:
        my_logger.debug("Downloading book cover for: {}".format(book['name']))
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
    my_logger.debug('Generating output')
    html = render_template(TEMPLATE_FILE, context={'books': books})
    with open(OUTPUT_FILE, 'w') as f:
        f.write(html)
    my_logger.debug('Output generation done!')
    my_logger.debug('Woooooot!')


def main():
    books = get_book_data()
    books = get_goodreads_data(books=books)
    books = download_book_covers(books=books)
    write_output(books=books)

    with open('output.json', 'w') as f:
        json.dump(obj=books, fp=f, indent=2)


if __name__ == '__main__':
    set_logger()
    my_logger.debug('----- starting the script -----')
    create_images_dir()
    main()
    my_logger.debug('----- bye, thanks for all the fish -----')
