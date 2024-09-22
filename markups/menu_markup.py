from aiogram import types
from aiogram.types import InlineKeyboardMarkup


async def main_menu_markup(user_id=None) -> InlineKeyboardMarkup:
    keyboard = []

    add_sub = types.InlineKeyboardButton(text='Добавить подписку', callback_data='add_subscription')
    all_subs = types.InlineKeyboardButton(text='Активные подписки', callback_data='add_subscription')
    keyboard.append([add_sub, all_subs])

    markup = types.InlineKeyboardMarkup(inline_keyboard=keyboard)

    return markup


async def back_to_menu_markup() -> InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')]])

    return markup
