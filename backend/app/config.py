import os

DATABASE_URL = os.getenv("DATABASE_URL")

ALERT_WEBHOOK_URL = os.getenv("ALERT_WEBHOOK_URL")

TIMEZONE = os.getenv("TIMEZONE", "Europe/Warsaw")
