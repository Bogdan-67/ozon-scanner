from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


class NewSubscription(StatesGroup):
    search = State()
    max_price = State()
