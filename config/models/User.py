from peewee import CharField, Model
from config.database.db import db


class User(Model):
    user_id = CharField(unique=True)

    class Meta:
        database = db
