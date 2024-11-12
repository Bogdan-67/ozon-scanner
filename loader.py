import asyncio
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import requests
from aiogram import Bot
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

if sys.version_info >= (3, 8) and sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')

load_dotenv()
admins = str(os.getenv('ADMINS')).split(',')

ADMINS_LIST = [int(admin) for admin in admins]

MODE = os.getenv('MODE')

BOT_API_TOKEN = os.getenv('BOT_TOKEN')

BOT_USERNAME = os.getenv('BOT_USERNAME')

EMAIL_SUPPORT_PASS = os.getenv('EMAIL_SUPPORT_PASS')

EMAIL_SUPPORT_LOGIN = os.getenv('EMAIL_SUPPORT_LOGIN')

EMAIL_SUPPORT_HOST = os.getenv('EMAIL_SUPPORT_HOST')

EMAIL_SUPPORT_PORT = os.getenv('EMAIL_SUPPORT_PORT')

storage = MemoryStorage()

sys.tracebacklimit = 0

logger = logging.getLogger(__name__)
level = logging.DEBUG if MODE != 'production' else logging.WARNING
logger.setLevel(level)

if logger.hasHandlers():
    logger.handlers.clear()

log_directory = 'logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file_path = os.path.join(log_directory, 'app.log')
# Создаем форматтер и применяем его к обработчику
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

rotating_handler = RotatingFileHandler(log_file_path, maxBytes=5000000, backupCount=5, encoding='utf-8')
rotating_handler.setLevel(level)
rotating_handler.setFormatter(formatter)

# Добавляем обработчик в логгер
logger.addHandler(rotating_handler)

# Создаем обработчик для вывода логов в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Создаем форматтер и применяем его к обработчику консоли
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# Добавляем обработчик консоли в логгер
logger.addHandler(console_handler)

logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("selenium").setLevel(logging.CRITICAL)
logging.getLogger("apscheduler").setLevel(logging.CRITICAL)