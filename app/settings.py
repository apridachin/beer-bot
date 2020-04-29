import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

UNTAPPD_ID = os.getenv("UNTAPPD_ID")
UNTAPPD_TOKEN = os.getenv("UNTAPPD_TOKEN")

REDIS_URL = os.getenv("REDIS_URL")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMINS = os.getenv("ADMINS")
DEVS = os.getenv("DEVS")

admins = ADMINS.split(",") if ADMINS else []
devs = list(map(lambda x: int(x), DEVS)) if DEVS else []

__all__ = ["TELEGRAM_TOKEN", "UNTAPPD_ID", "UNTAPPD_TOKEN", "admins", "devs", "REDIS_URL"]
