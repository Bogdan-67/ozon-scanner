import logging
import os

import requests
from aiogram.types import BufferedInputFile
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from retrying import retry
from bot import start_bot, bot
import time
import re

from config.database.notification_queries import find_notification, save_notification
from config.models.Subscription import Subscription
from helpers.seleniumHelper import get_uc_driver
from helpers.urlHelper import add_params_url
from markups.offer_markup import offer_markup

load_dotenv()


def search_ozon(query, max_price):
    driver = get_uc_driver()

    try:
        driver.get('https://www.ozon.ru/')
    except Exception as e:
        logging.error(f'Error open ozon page: {e}')
    time.sleep(3)

    # Поиск по запросу
    search_box = driver.find_element(By.XPATH, '//form[@action="/search"]/div/div[2]/input')  # Найдите правильный селектор
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(3)  # Ждем загрузки страницы

    # Установка фильтров (пример: по цене)
    # Найдите элементы фильтра и установите значения

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def enter_min_price():
        min_price_input = driver.find_elements(By.CSS_SELECTOR, 'input[class="d015-a d015-a0 e0115-a8"]')[0]
        min_price_input.clear()
        time.sleep(20)
        min_price_input.send_keys('30000')
        logging.debug("Минимальная цена введена успешно")

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def enter_max_price():
        max_price_input = driver.find_elements(By.CSS_SELECTOR, 'input[class="d015-a d015-a0 e0115-a8"]')[1]
        max_price_input.clear()
        max_price_input.send_keys(str(max_price))
        max_price_input.send_keys(Keys.RETURN)
        logging.debug("Максимальная цена введена успешно")

    try:
        enter_min_price()
    except Exception as e:
        logging.error("Ошибка при вводе минимальной цены после 5 попыток:", e)

    try:
        enter_max_price()
    except Exception as e:
        logging.error("Ошибка при вводе максимальной цены после 5 попыток:", e)

    time.sleep(3000)  # Ждем обновления результатов

    # Сбор информации о товарах
    products = driver.find_elements(By.CLASS_NAME, 'tile-root')  # Найдите правильный селектор для товаров
    logging.debug(products)
    result = []
    search_words = query.lower().split()

    for product in products:
        title = product.find_element(By.CLASS_NAME, 'tile-hover-target').text  # Найдите правильный селектор
        price = product.find_element(By.CLASS_NAME, 'c3015-c0').text  # Найдите правильный селектор
        link = product.find_element(By.TAG_NAME, 'a').get_attribute('href')

        # Преобразование цены в число
        price_value = int(re.sub(r'\D', '', price))

        if price_value <= max_price and all(word in title.lower() for word in search_words):
            result.append({
                'title': title,
                'price': price,
                'link': link
            })

    driver.quit()
    return result


def search_ozon_url(url: str, params: dict):
    driver = get_uc_driver()

    url = add_params_url(url, params)

    try:
        driver.get(url)
    except Exception as e:
        logging.error(f'Error open ozon page: {e}')
    time.sleep(3)

    # Сбор информации о товарах
    products = driver.find_elements(By.XPATH, '//div[contains(@class,"tile-root")]/div')  # Найдите правильный селектор для товаров
    print(products)
    result = []

    for product in products:
        try:
            info = product.find_element(By.CLASS_NAME, 'jr1_23')
            title = info.find_element(By.CLASS_NAME, 'tile-hover-target').text
            price = info.find_element(By.XPATH, './/span[contains(text(),"₽")]').text
            link = info.find_element(By.TAG_NAME, 'a').get_attribute('href')

            image_element = product.find_element(By.TAG_NAME, 'img')

            # Получаем атрибут src (URL изображения)
            image_url = image_element.get_attribute('src')

            result.append({
                'title': title,
                'price': price,
                'link': link,
                'image_url': image_url
            })
        except Exception as e:
            logging.error(f"Error: {e}")

    driver.quit()
    return result


async def check_sub_ozon(sub: Subscription):
    products = search_ozon_url(url=sub.url, params=sub.params) if sub.url else search_ozon(sub.search, sub.max_price)
    logging.debug(products)
    notys = []

    if products:
        try:
            for product in products:
                try:
                    if not await find_notification(title=product["title"], site='ozon'):
                        await save_notification(title=product["title"], user=sub.user, site='ozon')
                        message_text = f'{product["title"]} - {product["price"]}'
                        notys.append({
                            "image_url": product["image_url"],
                            "link": product["link"],
                            "message_text": message_text
                        })
                except Exception as e:
                    logging.error(e)

        except Exception as e:
            logging.error(e)

    return notys
