import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram import BaseMiddleware
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from dotenv import load_dotenv

load_dotenv()

from .database import Database
from .handlers import router
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_BASE = os.getenv("WEBHOOK_BASE")
REDIS_URL = os.getenv("REDIS_URL")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DbMiddleware(BaseMiddleware):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db

    async def __call__(self, handler, event, data):
        data["db"] = self.db
        return await handler(event, data)


def get_webhook_url() -> str:
    if not WEBHOOK_BASE:
        raise RuntimeError("WEBHOOK_BASE is required for webhook setup.")
    return WEBHOOK_BASE.rstrip("/") + "/webhook"


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(get_webhook_url())
    logger.info("Webhook set to %s", get_webhook_url())


async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Webhook deleted")


async def init_app() -> web.Application:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is required")
    if not REDIS_URL:
        raise RuntimeError("REDIS_URL is required")

    bot = Bot(BOT_TOKEN, parse_mode="HTML")
    db = Database(REDIS_URL)
    storage = RedisStorage.from_url(REDIS_URL)
    dp = Dispatcher(storage=storage)
    db_mw = DbMiddleware(db)
    dp.message.middleware(db_mw)
    dp.callback_query.middleware(db_mw)
    dp.include_router(router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    webhook_path = "/webhook"
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=webhook_path)
    setup_application(app, dp, bot=bot)
    return app


def main() -> None:
    port = int(os.getenv("PORT", "8080"))
    web.run_app(init_app(), host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
