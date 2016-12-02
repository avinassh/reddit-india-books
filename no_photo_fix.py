"""
(Stupid ass) Goodreads API response sometimes does not include the book cover
images even though cover images are present on their site. This script tries
to fix the issue by downloading the image from the site directly, without using
their API and then resizes the image

Book responses which do not have cover use the same stock image `nophoto`
"""
import os
import json
import time

import requests
from bs4 import BeautifulSoup
from PIL import Image
from resizeimage import resizeimage

from utils import download_image
from settings import IMAGES_DIR


def resize(source_image, target_image):
    source_image_path = os.path.join(IMAGES_DIR, source_image)
    target_image_path = os.path.join(IMAGES_DIR, target_image)
    with open(source_image_path, 'rb') as fd_img:
        img = Image.open(fd_img)
        img = resizeimage.resize_width(img, 98)
        img.save(target_image_path)


def download_book_cover(url, image_name):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    img_tag = soup.find('img', attrs={'id': 'coverImage'})
    if img_tag:
        image_url = img_tag.attrs['src']
        download_image(image_url=image_url, image_name=image_name)
        return True
    return False


def main():
    with open('output.json') as f:
        books = json.load(f)
    for book in books:
        if 'nophoto' in book['image_url']:
            image_name = book['image_name']
            full_size_image = "orig_{}".format(image_name)
            if download_book_cover(url=book['url'],
                                   image_name=full_size_image):
                resize(source_image=full_size_image, target_image=image_name)
        time.sleep(1)


if __name__ == '__main__':
    main()
