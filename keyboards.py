from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import PLANS, DAYS_LABEL, CHANNEL_LINK, ADMIN_USERNAME, SUPPORT_USERNAME_2
from locales import t


def lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
    ]])


def main_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_plans", lang),   callback_data="menu:plans")],
        [
            InlineKeyboardButton(text=t("btn_faq", lang),     callback_data="menu:faq"),
            InlineKeyboardButton(text=t("btn_support", lang), callback_data="menu:support"),
        ],
        [InlineKeyboardButton(text=t("btn_channel", lang), callback_data="menu:channel")],
    ])


def plans_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_ultimate", lang), callback_data="plan:ultimate")],
        [InlineKeyboardButton(text=t("btn_base", lang),     callback_data="plan:base")],
        [InlineKeyboardButton(text=t("back", lang),         callback_data="menu:back")],
    ])


def currency_keyboard(plan: str, lang: str) -> InlineKeyboardMarkup:
    text = "💰 В какой валюте оплатить?\n(GGshop использует ЮMoney)"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 RUB ₽", callback_data=f"currency:{plan}:RUB"),
            InlineKeyboardButton(text="🇺🇸 USD $", callback_data=f"currency:{plan}:USD"),
            InlineKeyboardButton(text="🇪🇺 EUR €", callback_data=f"currency:{plan}:EUR"),
        ],
        [InlineKeyboardButton(text=t("back", lang), callback_data="menu:plans")],
    ])


def periods_keyboard(plan: str, lang: str, currency: str = "RUB") -> InlineKeyboardMarkup:
    from config import CURRENCY_RATES, CURRENCY_SYMBOLS
    rows = []
    for days, price_rub in PLANS[plan].items():
        if days == "name":
            continue
        label = DAYS_LABEL[days][lang]
        rate = CURRENCY_RATES.get(currency, 1.0)
        symbol = CURRENCY_SYMBOLS.get(currency, "₽")
        if currency == "RUB":
            price_str = f"{price_rub} {symbol}"
        else:
            converted = round(price_rub * rate, 2)
            price_str = f"{converted} {symbol}"
        rows.append([InlineKeyboardButton(
            text=f"{label} — {price_str}",
            callback_data=f"period:{plan}:{days}:{currency}"
        )])
    rows.append([InlineKeyboardButton(text=t("back", lang), callback_data=f"plan:{plan}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_keyboard(plan: str, days: str, lang: str, currency: str = "RUB") -> InlineKeyboardMarkup:
    from config import CURRENCY_RATES, CURRENCY_SYMBOLS
    price_rub = PLANS[plan][days]
    rate = CURRENCY_RATES.get(currency, 1.0)
    symbol = CURRENCY_SYMBOLS.get(currency, "₽")
    if currency == "RUB":
        price_str = f"{price_rub} {symbol}"
    else:
        converted = round(price_rub * rate, 2)
        price_str = f"{converted} {symbol}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💳 Оплатить {price_str}", callback_data=f"confirm:{plan}:{days}:{currency}")],
        [InlineKeyboardButton(text=t("confirm_no", lang), callback_data=f"currency:{plan}:{currency}")],
        [InlineKeyboardButton(text=t("back", lang), callback_data="menu:plans")],
    ])


def pay_keyboard(url: str, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить / Pay", url=url)],
        [InlineKeyboardButton(text="🔄 Проверить оплату", callback_data="check_payment")],
        [InlineKeyboardButton(text=t("back", lang), callback_data="menu:plans")],
    ])


def back_keyboard(lang: str, target: str = "menu:back") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("back", lang), callback_data=target)]
    ])


def admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin:stats")],
        [InlineKeyboardButton(text="🎁 Выдать ключ бесплатно", callback_data="admin:givekey")],
        [InlineKeyboardButton(text="🗑 Удалить ключ", callback_data="admin:delkey")],
    ])
