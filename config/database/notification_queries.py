from config.database.db import objects
from config.models.Notification import Notification


async def find_notification(title, site):
    try:
        return await objects.get(Notification, (Notification.title == title) & (Notification.site == site))
    except Notification.DoesNotExist:
        return None
    except Exception as e:
        print('Database error:', e)
        raise


async def save_notification(title, user, site):
    try:
        Notification.create(title=title, user=user, site=site)
        return
    except Exception as e:
        print('Database error:', e)
        raise


async def delete_notification(date):
    try:
        await objects.execute(Notification.delete().where(Notification.last_updated < date))
        return
    except Exception as e:
        print('Database error:', e)
        raise