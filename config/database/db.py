import os

import peewee_async
from dotenv import load_dotenv

load_dotenv()

pg_user = os.getenv('PG_USER')
pg_pw = os.getenv('PG_PASSWORD')
pg_db = os.getenv('PG_DATABASE')
sv_host = os.getenv('SV_HOST')
pg_port = os.getenv('PG_PORT')

db = peewee_async.PostgresqlDatabase(
    'postgres',
    user=pg_user,
    password=pg_pw,
    host=sv_host,
    port=pg_port
)

objects = peewee_async.Manager(db)


async def create_pool():
    return db, objects
