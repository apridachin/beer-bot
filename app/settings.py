import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

TelegramToken = os.getenv("TELEGRAM_TOKEN")
BreweryToken = os.getenv("BREWERY_TOKEN")
Admins = os.getenv("ADMINS").split(",")
Devs = list(map(lambda x: int(x), os.getenv("DEVS").split(",")))

__all__ = ["TelegramToken", "BreweryToken", "Admins", "Devs"]
