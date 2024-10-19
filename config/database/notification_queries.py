from config.database.db import objects
from config.models.Notification import Notification


async def find_notification(link, site):
    try:
        return await objects.get(Notification, (Notification.link == link) & (Notification.site == site))
    except Notification.DoesNotExist:
        return None
    except Exception as e:
        print('Database error:', e)
        raise


async def save_notification(title, link, user, site):
    try:
        Notification.create(title=title, link=link, user=user, site=site)
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