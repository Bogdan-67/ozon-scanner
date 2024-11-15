from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import InputFile, FSInputFile, Message
from peewee import IntegrityError
from urllib.parse import urlparse, parse_qs

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
            data['user'] = message.from_user.id
            print(data)
            await save_subscription(data)
            await state.clear()

            await message.answer(f'Подписка на {data["search"]} добавлена ✅', parse_mode='html')
            await main_menu(message)
    except Exception as e:
        print(e)
        await message.answer(text='Что-то пошло не так 🙁\nПопробуйте еще раз позже')
        await main_menu(message)


@user_router.message(NewSubscription.url, F.content_type.in_({'text'}))
async def new_subscription_url(message: Message, state: FSMContext):
    print(message)
    try:
        parsed_url = urlparse(message.text.strip().lower())
        print(parsed_url)
        query_params = parse_qs(parsed_url.query)
        normalized_params = {key: value[0] if len(value) == 1 else value for key, value in query_params.items()}

        data = await state.get_data()
        data['origin_url'] = message.text.strip().lower()
        data['base_url'] = f'{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}{parsed_url.params}'
        data['user'] = message.from_user.id
        data['params'] = normalized_params
        print(data)
        await save_subscription(data)
        await state.clear()

        await message.answer(f'Подписка добавлена ✅', parse_mode='html')
        await main_menu(message)
    except Exception as e:
        print(e)
        await message.answer(text='Что-то пошло не так 🙁\nПопробуйте еще раз позже')
        await main_menu(message)
