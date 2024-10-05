from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


class NewSubscription(StatesGroup):
    site = State()
    url = State()
    search = State()
    max_price = State()
    params = State()
