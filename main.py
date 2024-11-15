import asyncio
import datetime
import os
import logging
from logging.handlers import RotatingFileHandler

import requests
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot import start_bot, bot
from config.database.notification_queries import delete_notification
from config.database.subscription_queries import get_user_subscriptions, delete_user_subscription, get_subscriptions
from config.routers.user_router import user_router
from loader import MODE, logger
from markups.offer_markup import offer_markup
from services.ozon import check_sub_ozon
from services.cian import check_sub_cian
from aiogram.filters import Command
from handlers.main_menu import main_menu
from aiogram import Bot, Dispatcher, types, html
from markups.menu_markup import back_to_menu_markup
from markups.sites_markup import sites_markup
from states.DeleteSubState import DeleteSubState
from states.NewSubscription import NewSubscription
import sys
from const.sites import SITES
from dateutil.relativedelta import relativedelta

import handlers.new_subscription_handler
import handlers.main_menu
import handlers.delete_subscription_handler

load_dotenv()


@user_router.message(Command('start'))
async def start(message: types.Message):
    first_mess = f"<b>{message.from_user.first_name}</b>, привет!"
    await message.answer(first_mess, parse_mode='html')
    await main_menu(message)


@user_router.message(Command('menu'))
async def menu(message: types.Message):
    await main_menu(message)


@user_router.callback_query()
async def response(callback: types.CallbackQuery, state: FSMContext):
    print(callback.data)
    if callback.message.chat.type == 'private':

        if callback.data == "menu":
            await main_menu(callback.message, callback.from_user)

        elif callback.data == "add_subscription":
            mess = 'Выбери сервис для отслеживания'
            await callback.message.answer(mess, reply_markup=sites_markup())

        elif callback.data in [site['code'] for site in SITES]:
            await state.set_state(NewSubscription.site)
            await state.update_data(site=callback.data)

            mess = 'Ссылка на страницу с выставленными фильтрами'
            await state.set_state(NewSubscription.url)
            await callback.message.answer(mess)

        elif callback.data == "subscriptions":
            subscriptions = await get_user_subscriptions(callback.from_user.id)

            if len(subscriptions) == 0:
                await callback.message.answer("Нет активных подписок")
                return

            mess = "Список активных подписок:\n" + "\n".join(
                [f"{i+1}. {sub.site} - {sub.origin_url}" for i, sub in enumerate(subscriptions)])
            markup = types.InlineKeyboardMarkup(
                inline_keyboard=[[types.InlineKeyboardButton(text='Удалить подписку', callback_data='delete_sub')]])

            await callback.message.answer(text=mess, reply_markup=markup, disable_web_page_preview=True)

        elif callback.data == 'delete_sub':
            mess = 'Введи номер подписки, которую удалить'
            await state.set_state(DeleteSubState.waiting_for_subscription_number)
            await callback.message.answer(text=mess)


async def job():
    subs = await get_subscriptions()
    for sub in subs:
        notifications = []
        try:
            match sub.site:
                case 'ozon':
                    notifications = await check_sub_ozon(sub)
                case 'cian':
                    notifications = await check_sub_cian(sub)
            send_num = 0
            for noty in notifications:
                try:
                    image = None
                    try:
                        # Скачиваем изображение с использованием requests и сохраняем его в памяти
                        image_data = requests.get(noty["image_url"]).content
                        image = BufferedInputFile(file=image_data, filename='image.png')
                    except requests.exceptions.InvalidSchema as e:
                        # Логируем исключение правильно
                        logger.error("Error get image: %s", str(e))

                    if image:
                        await bot.send_photo(chat_id=sub.user, photo=image, caption=noty["message_text"],
                                             reply_markup=offer_markup(noty["link"]), parse_mode='html')
                    else:
                        await bot.send_message(chat_id=sub.user, text=noty["message_text"],
                                               reply_markup=offer_markup(noty["link"]), parse_mode='html')
                    send_num += 1
                except Exception as e:
                    logger.error('Error send notification: %s', str(e))
            logger.debug(f"Sended {send_num} of {len(notifications)} notifications")
        except Exception as e:
            logger.error('Error get notifications for sub %s: %s', sub.id, str(e))


async def clear_db():
    now = datetime.datetime.now()
    delete_date = now - relativedelta(months=2)

    await delete_notification(delete_date)


async def main():
    logging.info("Скрипт запущен. Нажмите Ctrl+C для остановки.")
    bot_task = asyncio.create_task(start_bot())
    await clear_db()
    # await job()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(job, 'interval', hours=1)
    scheduler.add_job(clear_db, 'interval', hours=24)
    scheduler.start()

    await bot_task


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Application shutdown")
