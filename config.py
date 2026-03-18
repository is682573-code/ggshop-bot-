import os
from dotenv import load_dotenv

load_dotenv()

# ─── Telegram ───────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "8680066893:AAGNe59MkOppS65bPSz-uHIHpsZviLA48rI")
ADMIN_ID = int(os.getenv("ADMIN_ID", "5712869308"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "@llostikKJ00")
SUPPORT_USERNAME_2 = "@cha7ok"
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/YOURCHANNELHERE")  # заполни позже

# ─── Database ───────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/ggshop")

# ─── YooMoney ───────────────────────────────────────────────
YOOMONEY_TOKEN = os.getenv(
    "YOOMONEY_TOKEN",
    "4100119480343964.F99CA19C679B67E0F8692F20B1C40927C8CCDAA492F4144D3B31CA4D744E8867B3BC550CE62E27B44E0348788ABE4AC2B6DC49722099A24D760203AAA754CAFF108A8F4199FFBBC5F1D758DF629090E0FD9B1738FC572AA4BA720CFA10D0996AEEC1A6A0193832964DA39A32B8D3A02A3ED746858CBD2FC6015DAA09E392790A"
)
YOOMONEY_WALLET = os.getenv("YOOMONEY_WALLET", "4100119480343964")
YOOMONEY_SECRET = os.getenv("YOOMONEY_SECRET", "")  # notification_secret из кабинета ЮМани

# ─── Key Server ─────────────────────────────────────────────
KEY_SERVER_BASE = "https://key-server-production-87e7.up.railway.app"
KEY_SERVER_CHECK = KEY_SERVER_BASE + "/check?user="
KEY_SERVER_ADD   = KEY_SERVER_BASE + "/add?user="      # добавишь параметры сам
KEY_SERVER_DELETE = KEY_SERVER_BASE + "/delete?user="

# ─── Webhook (Railway выдаёт PUBLIC_URL автоматически) ──────
WEBHOOK_HOST = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL  = f"https://{WEBHOOK_HOST}{WEBHOOK_PATH}" if WEBHOOK_HOST else ""
WEBAPP_HOST  = "0.0.0.0"
WEBAPP_PORT  = int(os.getenv("PORT", 8080))

# ─── Тарифы ─────────────────────────────────────────────────
PLANS = {
    "ultimate": {
        "name": "Ultimate 👑",
        "7":   59,
        "30":  250,
        "999": 760,   # 999 = навсегда
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
