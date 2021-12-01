import asyncio
import logging

from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import config
from db.base import Base
from middlewares.db import DbMiddleware
from viberio.dispatcher.webhook import ViberWebhookView

from loader import app, viber, loop, scheduler
from handlers import dp

# logging.basicConfig(level=logging.DEBUG)
ViberWebhookView.bind(dp, app, '/')


async def set_webhook():
    await asyncio.sleep(1)
    print("setting webhook")
    result = await viber.set_webhook(config.WEBHOOK_URL, webhook_events=[
        # "delivered",
        # "seen",
        # "failed",
        # "subscribed",
        # "unsubscribed",
        "conversation_started"])


async def on_shutdown(application: web.Application):
    await viber.unset_webhook()
    await viber.close()


async def on_startup(application: web.Application):
    print("on_stratup")
    # DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/foryou_storyes"
    # DATABASE_URL = "sqlite+aiosqlite://"
    DATABASE_URL = "sqlite+aiosqlite:///sqlalchemy.db"
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    dp.middleware.setup(DbMiddleware(async_session))


if __name__ == '__main__':
    scheduler.start()
    app.on_startup.append(on_startup)
    loop.create_task(set_webhook())
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host='0.0.0.0', port=5000)
