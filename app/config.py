import os

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Config(BaseSettings):
    CLIENT_ID = os.getenv('CLIENT_ID', '')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET', '')
    REDIRECT_URI = os.getenv('REDIRECT_URI', '')
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    BOT_USERNAME = os.getenv('BOT_USERNAME', '')
    BOT_TOKEN = os.getenv('BOT_TOKEN', '')


config = Config()

