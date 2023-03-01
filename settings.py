import os

from pydantic import BaseSettings


class Settings(BaseSettings):
	TELEGRAM_TOKEN: str = '6033291608:AAFQNeCgfrZfV1btOZwYMqNNFvZfwVn11Ak'
	BASE_DIR = os.path.dirname(os.path.realpath(__file__))


settings = Settings()
