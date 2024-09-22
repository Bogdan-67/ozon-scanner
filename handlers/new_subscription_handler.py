from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import InputFile, FSInputFile, Message
from peewee import IntegrityError

from config.database.subscription_queries import save_subscription
from config.routers.user_router import user_router
from main import main_menu

from states.NewSubscription import NewSubscription


@user_router.message(NewSubscription.search, F.content_type.in_({'text'}))
async def new_subscription(message: Message, state: FSMContext):
    print(message)
    try:
        await state.update_data(search=message.text.strip().lower())
        await state.set_state(NewSubscription.max_price)

        await message.answer(text="Максимальная цена:")
    except Exception as e:
        print(e)
        await message.answer(text='Что-то пошло не так 🙁\nПопробуйте еще раз позже')
        await main_menu(message)


@user_router.message(NewSubscription.max_price)
async def new_subscription(message: Message, state: FSMContext):
    try:
        price = message.text.strip()
        if not price.isdigit():
            await message.answer(text='Некорректный тип данных')
        else:
            await state.update_data(max_price=price)

            data = await state.get_data()
            print(data)
            await save_subscription(data['search'], data['max_price'], message.from_user.id)
            await state.clear()

            await message.answer(f'Подписка на {data["search"]} добавлена ✅', parse_mode='html')
            await main_menu(message)
    except Exception as e:
        print(e)
        await message.answer(text='Что-то пошло не так 🙁\nПопробуйте еще раз позже')
        await main_menu(message)
