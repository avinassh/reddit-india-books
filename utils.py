import os
import shutil

import requests

from settings import IMAGES_DIR


def _check_image_exists(file_name):
    return os.path.isfile(os.path.join(IMAGES_DIR, file_name))


def download_image(image_url, image_name):
    if _check_image_exists(file_name=image_name):
        return
    image_path = os.path.join(IMAGES_DIR, image_name)
    r = requests.get(image_url, stream=True)
    if r.status_code == 200:
        with open(image_path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
