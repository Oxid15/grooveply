import os

VERSION = "0.1.0"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(BASE_DIR, "grooveply.db")
TZ = "Europe/Moscow"
