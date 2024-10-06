from peewee import Model, AutoField, CharField, DateTimeField
from config.database.db import db
import datetime


class Notification(Model):
    id: int | AutoField = AutoField()
    user: str | CharField = CharField()
    title: str | CharField = CharField()
    site: str | CharField = CharField()
    last_updated = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
