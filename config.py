import os
from dotenv import load_dotenv

load_dotenv()

# ─── Telegram ───────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "8680066893:AAGNe59MkOppS65bPSz-uHIHpsZviLA48rI")
ADMIN_ID = int(os.getenv("ADMIN_ID", "5712869308"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "@llostikKJ00")
SUPPORT_USERNAME_2 = "@cha7ok"
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/YOURCHANNELHERE")

# ─── Database ───────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/ggshop")

# ─── YooMoney ───────────────────────────────────────────────
YOOMONEY_TOKEN = os.getenv("YOOMONEY_TOKEN", "")
YOOMONEY_WALLET = os.getenv("YOOMONEY_WALLET", "4100119480343964")
YOOMONEY_SECRET = os.getenv("YOOMONEY_SECRET", "")

# ─── Key Server ─────────────────────────────────────────────
KEY_SERVER_BASE = "https://key-server-production-87e7.up.railway.app"
KEY_SERVER_CHECK  = KEY_SERVER_BASE + "/check?user="
KEY_SERVER_ADD    = KEY_SERVER_BASE + "/add?user="
KEY_SERVER_DELETE = KEY_SERVER_BASE + "/delete?user="

# ─── Webhook ────────────────────────────────────────────────
WEBHOOK_HOST = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL  = f"https://{WEBHOOK_HOST}{WEBHOOK_PATH}" if WEBHOOK_HOST else ""
WEBAPP_HOST  = "0.0.0.0"
WEBAPP_PORT  = int(os.getenv("PORT", 8080))

# ─── Тарифы (цены всегда в RUB) ─────────────────────────────
PLANS = {
    "ultimate": {
        "name": "Ultimate 👑",
        "7":   59,
        "30":  250,
        "999": 760,
    },
    "base": {
        "name": "Base ⚡",
        "7":   45,
        "30":  130,
        "999": 450,
    },
}

DAYS_LABEL = {
    "7":   {"ru": "7 дней",   "en": "7 days"},
    "30":  {"ru": "30 дней",  "en": "30 days"},
    "999": {"ru": "Навсегда", "en": "Forever"},
}

# ─── Валюты ─────────────────────────────────────────────────
CURRENCY_RATES = {
    "RUB": 1.0,
    "USD": 0.011,
    "EUR": 0.010,
}

CURRENCY_SYMBOLS = {
    "RUB": "₽",
    "USD": "$",
    "EUR": "€",
}
