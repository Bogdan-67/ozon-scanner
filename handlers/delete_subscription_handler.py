from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config.database.subscription_queries import get_user_subscriptions, delete_user_subscription
from config.routers.user_router import user_router
from loader import logger
from states.DeleteSubState import DeleteSubState


@user_router.message(DeleteSubState.waiting_for_subscription_number)
async def delete_sub(message: Message, state: FSMContext):
    num = message.text
    if num.isdigit():
        try:
            subs = await get_user_subscriptions(message.from_user.id)
            await delete_user_subscription(subs[int(num)-1])
            await message.answer(text='Подписка удалена ✅')
        except Exception as e:
            logger.error(e)
            await message.answer(text='Что-то пошло не так 🙁\nПопробуйте еще раз позже')
        finally:
            await state.clear()
    else:
        await message.answer(text="Неверный номер, попробуй снова", callback="selected_deletion")