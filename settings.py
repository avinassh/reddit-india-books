import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, 'dist')
IMAGES_DIR = os.path.join(DIST_DIR, 'images')
SOURCE_FILE = os.path.join(BASE_DIR, 'source.txt')
OUTPUT_FILE = os.path.join(DIST_DIR, 'index.html')

# Logging settings
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILENAME = os.path.join(LOG_DIR, 'output_log')
