from aiogram.fsm.state import StatesGroup, State


class DeleteSubState(StatesGroup):
    waiting_for_subscription_number = State()