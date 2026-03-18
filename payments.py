import hashlib
import hmac
import uuid
import logging
import aiohttp
from urllib.parse import urlencode
from config import YOOMONEY_WALLET, YOOMONEY_TOKEN, YOOMONEY_SECRET, KEY_SERVER_ADD

logger = logging.getLogger(__name__)


def generate_label() -> str:
    """Уникальный label для платежа — по нему ЮМани шлёт webhook."""
    return str(uuid.uuid4())


def build_payment_url(amount: float, label: str, comment: str = "GGshop XENO") -> str:
    """
    Генерирует ссылку на форму оплаты ЮМани (quickpay).
    Пользователь переходит по ней и платит — ЮМани шлёт webhook на /yoomoney.
    """
    params = {
        "receiver":     YOOMONEY_WALLET,
        "quickpay-form": "button",
        "paymentType":  "AC",          # AC = банковская карта, PC = кошелёк ЮМани
        "sum":          amount,
        "label":        label,
        "comment":      comment,
        "successURL":   "",            # можно добавить позже
    }
    return "https://yoomoney.ru/quickpay/confirm?" + urlencode(params)


def verify_webhook(data: dict) -> bool:
    """
    Проверка подписи входящего webhook от ЮМани.
    https://yoomoney.ru/docs/payment-buttons/using-api/notifications
    """
    if not YOOMONEY_SECRET:
        logger.warning("YOOMONEY_SECRET не задан — пропускаем проверку подписи!")
        return True

    keys = [
        "notification_type", "operation_id", "amount",
        "currency", "datetime", "sender", "codepro", "label",
    ]
    check_str = "&".join(str(data.get(k, "")) for k in keys) + "&" + YOOMONEY_SECRET
    sha1 = hashlib.sha1(check_str.encode()).hexdigest()
    return sha1 == data.get("sha1_hash", "")


async def add_key_to_server(roblox_username: str, days: str) -> bool:
    """
    Добавляет username на key-сервер после успешной оплаты.
    Эндпоинт /add — добавишь параметры days/plan сам при необходимости.
    """
    url = KEY_SERVER_ADD + roblox_username
    # Если key-сервер принимает days: url += f"&days={days}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                text = await resp.text()
                logger.info(f"Key server /add response for {roblox_username}: {text}")
                return resp.status == 200
    except Exception as e:
        logger.error(f"Key server /add error: {e}")
        return False


async def delete_key_from_server(roblox_username: str) -> bool:
    from config import KEY_SERVER_DELETE
    url = KEY_SERVER_DELETE + roblox_username
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                text = await resp.text()
                logger.info(f"Key server /delete response for {roblox_username}: {text}")
                return resp.status == 200
    except Exception as e:
        logger.error(f"Key server /delete error: {e}")
        return False
