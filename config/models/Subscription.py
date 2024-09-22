from peewee import Model, AutoField, CharField, DateTimeField, DecimalField
from config.database.db import db
import datetime


class Subscription(Model):
    id = AutoField()
    search = CharField()
    max_price = DecimalField()
    user = CharField()
    last_updated = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
