from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
from peewee import Database
from peewee_async import Manager


class DbMiddleware(BaseMiddleware):
    def __init__(self, db: Database, objects: Manager) -> None:
        self.db = db
        self.objects = objects

    async def __call__(self,
                        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                        event: Message, data: Dict[str, Any]) -> Any:
        with self.db.connection_context():
            data['db'] = self.db
            data['objects'] = self.objects
            return await handler(event, data)