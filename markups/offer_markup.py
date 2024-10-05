from aiogram import types


def offer_markup(url):
    keyboard = []

    link = types.InlineKeyboardButton(text='Перейти', url=url)
    keyboard.append([link])

    markup = types.InlineKeyboardMarkup(inline_keyboard=keyboard)

    return markup
