import asyncio
import os
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot import start_bot, bot
from config.database.subscription_queries import get_user_subscriptions, delete_user_subscription, get_subscriptions
from config.routers.user_router import user_router
from services.search_ozon import search_ozon
from aiogram.filters import Command
from handlers.main_menu import main_menu
from aiogram import Bot, Dispatcher, types, html
from markups.menu_markup import back_to_menu_markup
from states.NewSubscription import NewSubscription
import sys

import handlers.new_subscription_handler
import handlers.main_menu

if sys.version_info >= (3, 8) and sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

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
            mess = 'Поисковый запрос:'
            await state.set_state(NewSubscription.search)
            await callback.message.answer(mess, parse_mode='html')
            print('message send')

        elif callback.data == "subscriptions":
            subscriptions = await get_user_subscriptions(callback.from_user.id)
            mess = "Список активных подписок:" + "\n".join([f"{index + 1}. {sub['search']} - {sub['max_price']}" for sub, index in subscriptions])
            markup = types.InlineKeyboardMarkup(
                inline_keyboard=[[types.InlineKeyboardButton(text='Удалить подписку', callback_data='delete_sub')]])

            await callback.message.answer(text=mess, reply_markup=markup)

        elif callback.data == 'delete_sub':
            mess = 'Введи номер подписки, которую удалить'
            await callback.message.answer(text=mess, callback="selected_deletion")

        elif callback.data == 'selected_deletion':
            num = callback.message.text
            if num.isdigit():
                try:
                    subs = await get_user_subscriptions(callback.from_user.id)
                    await delete_user_subscription(subs[num])
                except Exception as e:
                    print(e)
                    await callback.message.answer(text='Что-то пошло не так 🙁\nПопробуйте еще раз позже')
            else:
                await callback.message.answer(text="Неверный номер, попробуй снова", callback="selected_deletion")


async def job():
    subs = await get_subscriptions()
    for sub in subs:
        products = search_ozon(sub.search, sub.max_price)

        if products:
            try:
                await bot.send_message(chat_id=sub.user, text="Найдены товары по вашей цене")
                # body = "\n\n".join([f'{product["title"]} - {product["price"]}\n{product["link"]}' for product in products])
                # send_email("Найдены товары по вашей цене", body)

                for product in products:
                    try:
                        message_text = f'{product["title"]} - {product["price"]}\n{product["link"]}'
                        await bot.send_message(chat_id=sub.user, text=message_text)
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)
    else:
        print("Товары не найдены")


async def main():
    print("Скрипт запущен. Нажмите Ctrl+C для остановки.")
    bot_task = asyncio.create_task(start_bot())
    await job()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(job, 'interval', hours=2)
    scheduler.start()

    await bot_task


if __name__ == "__main__":
    asyncio.run(main())
