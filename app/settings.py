import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

TelegramToken = os.getenv("TELEGRAM_TOKEN")
BreweryToken = os.getenv("BREWERY_TOKEN")
ADMINS = os.getenv("ADMINS")
DEVS = os.getenv("DEVS")

admins = ADMINS.split(",") if ADMINS else []
devs = list(map(lambda x: int(x), DEVS)) if DEVS else []

__all__ = ["TelegramToken", "BreweryToken", "admins", "devs"]
