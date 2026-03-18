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


def periods_keyboard(plan: str, lang: str) -> InlineKeyboardMarkup:
    rows = []
    for days, price in PLANS[plan].items():
        if days == "name":
            continue
        label = DAYS_LABEL[days][lang]
        rows.append([InlineKeyboardButton(
            text=f"{label} — {price} руб.",
            callback_data=f"period:{plan}:{days}"
        )])
    rows.append([InlineKeyboardButton(text=t("back", lang), callback_data="menu:plans")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_keyboard(plan: str, days: str, lang: str) -> InlineKeyboardMarkup:
    price = PLANS[plan][days]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("pay_button", lang, price=price), callback_data=f"confirm:{plan}:{days}")],
        [InlineKeyboardButton(text=t("confirm_no", lang), callback_data=f"plan:{plan}")],
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
