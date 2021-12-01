import asyncio

from aiohttp import web
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
from viberio.api.client import ViberBot
from viberio.dispatcher.dispatcher import Dispatcher
from viberio.types import BotConfiguration

loop = asyncio.get_event_loop()
app = web.Application()
bot_config = BotConfiguration(auth_token=config.API_TOKEN,
                              name=config.BOT_NAME,
                              avatar=config.AVATAR)
viber = ViberBot(bot_config)
dp = Dispatcher(viber)
jobstores = {
    # 'default': SQLAlchemyJobStore(url='sqlite:///aps_scheduler_jobs.sqlite')
    'default': SQLAlchemyJobStore(url='sqlite://')
}
scheduler = AsyncIOScheduler(jobstores=jobstores)
