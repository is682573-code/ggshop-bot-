import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from database import init_db
from handlers.start import router as start_router
from handlers.shop import router as shop_router
from handlers.admin import router as admin_router
from handlers.webhook import yoomoney_webhook

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    await init_db()
    if WEBHOOK_URL:
        await bot.set_webhook(WEBHOOK_URL + "/bot")
        logger.info(f"✅ Webhook set: {WEBHOOK_URL}/bot")
    else:
        logger.info("⚠️ WEBHOOK_URL not set — falling back to polling")


async def on_shutdown(bot: Bot):
    if WEBHOOK_URL:
        await bot.delete_webhook()


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp  = Dispatcher(storage=MemoryStorage())

    dp.include_router(start_router)
    dp.include_router(shop_router)
    dp.include_router(admin_router)

    if WEBHOOK_URL:
        # ── Webhook mode (Railway) ───────────────────────────
        from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

        app = web.Application()
        app["bot"] = bot  # для yoomoney_webhook

        # YooMoney уведомления
        app.router.add_post("/yoomoney", yoomoney_webhook)

        # Telegram webhook
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH + "/bot")
        setup_application(app, dp, bot=bot)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)

        await on_startup(bot)
        logger.info(f"🚀 Bot running on {WEBAPP_HOST}:{WEBAPP_PORT}")
        await site.start()

        # Держим сервер живым
        await asyncio.Event().wait()

    else:
        # ── Polling mode (локальная разработка) ─────────────
        await on_startup(bot)
        logger.info("🔄 Polling mode started")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
