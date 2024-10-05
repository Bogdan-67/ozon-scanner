from jsonfield.jsonfield import JSONField
from peewee import Model, AutoField, CharField, DateTimeField, DecimalField
from config.database.db import db
import datetime


class Subscription(Model):
    id: int | AutoField = AutoField()
    search: str | CharField = CharField(null=True)
    max_price: float | DecimalField = DecimalField(null=True)
    user: str | CharField = CharField()
    site: str | CharField = CharField(null=True)
    url: str | CharField = CharField(null=True)
    params: dict | JSONField = JSONField(null=True)
    last_updated = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
