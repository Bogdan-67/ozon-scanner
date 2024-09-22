from config.database.db import objects
from config.models.Subscription import Subscription
import asyncpg


async def get_subscriptions():
    try:
        subscriptions = await objects.execute(Subscription.select())
        print('response:', list(subscriptions))
        return list(subscriptions)
    except Exception as e:
        print('error', e)
        raise


async def get_user_subscriptions(user_id):
    try:
        subscriptions = await objects.get(Subscription, Subscription.user == user_id)
        print('response:', list(subscriptions))
        return list(subscriptions)
    except Exception as e:
        print('error', e)
        raise


async def delete_user_subscription(subscription):
    try:
        await objects.execute(Subscription.delete().where(Subscription.id == subscription.id and Subscription.user == subscription.user))
        return
    except Exception as e:
        print('error', e)
        raise


async def save_subscription(search: str, max_price: str, user: int):
    try:
        await objects.create(Subscription, search=search, max_price=max_price, user=user)
        return
    except Exception as e:
        print(e)
        raise