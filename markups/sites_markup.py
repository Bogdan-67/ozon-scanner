from aiogram import types
from const.sites import SITES


def sites_markup():
    buttons = [types.InlineKeyboardButton(text=site['name'], callback_data=site['code']) for site in SITES]

    elems = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    # cancel = types.KeyboardButton(text="Вернуться назад")
    # elems.append([cancel])
    markup = types.InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=elems)

    return markup