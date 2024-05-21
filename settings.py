from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv('PG_USER')
PASSWORD = os.getenv('PG_PASSWORD')
PORT = os.getenv('PG_PORT')
NAME_DB = os.getenv('PG_DATABASE')
HOST = os.getenv('PG_HOST')

KEY_BOT=os.getenv('KEY_BOT')
KEY_WEATHER=os.getenv('KEY_WEATHER')
KEY_YANDEX_MAP=os.getenv('KEY_YANDEX_MAP')