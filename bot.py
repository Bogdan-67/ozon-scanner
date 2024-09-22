import asyncio
import os
from dotenv import load_dotenv
from aiogram import Dispatcher, Bot

from config import middleware
from config.database.db import create_pool
from config.models.Subscription import Subscription
from config.models.User import User
from config.routers.user_router import user_router

load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))


async def start_bot():
    dp = Dispatcher()

    dp.include_router(user_router)
    database, objects = await create_pool()

    with database:
        database.create_tables([User, Subscription])

    user_router.message.middleware(middleware.DbMiddleware(db=database, objects=objects))
    user_router.callback_query.middleware(middleware.DbMiddleware(db=database, objects=objects))

    await dp.start_polling(bot, allowed_updates=["message", 'inline_query', "callback_query"])

if __name__ == "__main__":
    asyncio.run(start_bot())
