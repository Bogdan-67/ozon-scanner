from config.database.db import objects
from config.models.Subscription import Subscription
import asyncpg
import json


async def get_subscriptions():
    try:
        subscriptions = await objects.execute(Subscription.select())
        print(list(subscriptions))
        return subscriptions
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


async def save_subscription(data_dict: dict):
    try:
        if 'params' in data_dict:
            data_dict['params'] = json.dumps(data_dict['params'])

        Subscription.create(**data_dict)
        return
    except Exception as e:
        print(e)
        raise
