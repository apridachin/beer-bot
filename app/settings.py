import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

TelegramToken = os.getenv('TELEGRAM_TOKEN')
BreweryToken = os.getenv('BREWERY_TOKEN')

__all__ = ['TelegramToken', 'BreweryToken']