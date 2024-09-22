from markups.menu_markup import main_menu_markup

async def main_menu(message, from_user=None):
    if from_user is None:
        from_user = message.from_user

    mess = 'Выбери действие'

    markup = await main_menu_markup(from_user.id)

    await message.answer(mess, reply_markup=markup)