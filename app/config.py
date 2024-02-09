import os

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Config(BaseSettings):
    BOT_TOKEN = os.getenv('BOT_TOKEN', '')
    BOT_USERNAME = os.getenv('BOT_USERNAME', '')

    CLIENT_ID = os.getenv('CLIENT_ID', '')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET', '')
    REDIRECT_URI = os.getenv('REDIRECT_URI', '')

    DATABASE_URL = os.getenv('DATABASE_URL', '')
    DEFAULT_AVATAR = os.getenv('DEFAULT_AVATAR', '')


config = Config()

