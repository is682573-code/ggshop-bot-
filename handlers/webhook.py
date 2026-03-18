import logging
from aiohttp import web
from aiogram import Bot

from config import ADMIN_ID, PLANS, DAYS_LABEL, ADMIN_USERNAME
from database import get_purchase_by_label, mark_paid
from payments import verify_webhook, add_key_to_server
from locales import t

logger = logging.getLogger(__name__)


async def yoomoney_webhook(request: web.Request) -> web.Response:
    bot: Bot = request.app["bot"]

    try:
        data = await request.post()
        data = dict(data)
        logger.info(f"YooMoney webhook received: {data}")
    except Exception as e:
        logger.error(f"Webhook parse error: {e}")
        return web.Response(status=400)

    # Проверка подписи
    if not verify_webhook(data):
        logger.warning("Webhook signature mismatch!")
        return web.Response(status=403)

    label        = data.get("label", "")
    amount       = float(data.get("amount", 0))
    notification = data.get("notification_type", "")

    if not label:
        return web.Response(status=200)

    purchase = await get_purchase_by_label(label)
    if not purchase:
        logger.warning(f"Purchase not found for label: {label}")
        return web.Response(status=200)

    if purchase["status"] == "paid":
        return web.Response(status=200)  # уже обработано

    # Проверяем сумму (допуск 1 рубль на случай комиссии)
    if amount < purchase["price"] - 1:
        logger.warning(f"Amount mismatch: got {amount}, expected {purchase['price']}")
        return web.Response(status=200)

    await mark_paid(label)

    roblox  = purchase["roblox_user"]
    plan    = purchase["plan"]
    days    = purchase["days"]
    tg_id   = purchase["tg_id"]
    price   = purchase["price"]

    # Определяем язык пользователя
    from database import get_user_lang
    lang = await get_user_lang(tg_id)
    period    = DAYS_LABEL[days][lang]
    plan_name = PLANS[plan]["name"]

    # Добавляем ключ на сервер
    ok         = await add_key_to_server(roblox, days)
    key_status = t("key_added", lang, username=roblox) if ok else t("key_error", lang, username=roblox)

    # Сообщение пользователю
    try:
        await bot.send_message(
            tg_id,
            t("payment_success", lang,
              username=roblox,
              plan=plan_name,
              period=period,
              support=ADMIN_USERNAME),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to send key to user {tg_id}: {e}")

    # Уведомление администратору
    try:
        await bot.send_message(
            ADMIN_ID,
            f"💰 <b>Новая оплата!</b>\n\n"
            f"👤 TG ID: <code>{tg_id}</code>\n"
            f"🎮 Roblox: <code>{roblox}</code>\n"
            f"📦 Тариф: {plan_name}\n"
            f"⏳ Период: {period}\n"
            f"💳 Сумма: {price} руб.\n\n"
            f"{key_status}",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")

    return web.Response(status=200)
