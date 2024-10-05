import os
from io import BytesIO

import requests
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from retrying import retry
from aiogram.types import InputFile, BufferedInputFile
from bot import start_bot, bot
import time
import re
from helpers.seleniumHelper import get_uc_driver
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs

from helpers.textHelper import truncate_text
from helpers.urlHelper import add_params_url
from markups.offer_markup import offer_markup

load_dotenv()


async def search_cian(params):
    base_url = 'https://www.cian.ru/cat.php'

    url = add_params_url(base_url, params)

    driver = get_uc_driver()
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        });
        '''})

    try:
        driver.get(url)
    except Exception as e:
        print(f'Error open page: {e}')

    time.sleep(3)

    try:
        offers = driver.find_elements(By.XPATH, '//div[contains(@data-testid,"offer-card")]')
        print(offers)
        result = []

        for offer in offers:
            try:
                title = offer.find_element(By.XPATH, './/span[@data-mark="OfferTitle"]/span').text
                location = offer.find_element(By.XPATH, './/div[@class="_93444fe79c--labels--L8WyJ"]').text
                price = offer.find_element(By.XPATH, './/span[@data-mark="MainPrice"]/span').text
                price_info = offer.find_element(By.XPATH, './/p[@data-mark="PriceInfo"]').text
                link = offer.find_element(By.TAG_NAME, 'a').get_attribute('href')
                description = offer.find_element(By.XPATH, './/div[contains(@data-name,"Description")]/p').text
                author = offer.find_element(By.XPATH, './/div[contains(@data-name,"BrandingLevelWrapper")]/div/div[contains(@class,"content")]/div/div/div/span').text

                image_element = offer.find_element(By.TAG_NAME, 'img')

                # Получаем атрибут src (URL изображения)
                image_url = image_element.get_attribute('src')

                other_content_length = len(title) + len(location) + len(price) + len(price_info) + len(author)

                # Рассчитываем оставшееся количество символов для description
                available_length_for_description = 1002 - other_content_length

                # Если длина description превышает допустимое значение, обрезаем его
                if len(description) > available_length_for_description:
                    description = description[:available_length_for_description - 3] + '...'

                result.append({
                    'title': title,
                    'location': location,
                    'price': price,
                    'price_info': price_info,
                    'link': link,
                    'description': description,
                    'author': author,
                    'image_url': image_url
                })
            except Exception as e:
                print(f"Error: {e}")

        driver.quit()
        return result
    except Exception as e:
        raise f'Error get cian offers: {e}'


async def check_sub_cian(sub):
    try:
        offers = await search_cian(sub.params)
        print('offers:', offers)

        if offers:
            try:
                await bot.send_message(chat_id=sub.user, text="Найдены объявления по вашему запросу")

                for offer in offers:
                    try:
                        message_text = f'{offer["title"]} - {offer["price"]}\n{offer["price_info"]}\n{offer["location"]}\nАвтор: {offer["author"]}\n\n<i>{offer["description"]}</i>'

                        # Скачиваем изображение с использованием requests и сохраняем его в памяти
                        image_data = requests.get(offer["image_url"]).content
                        image = BufferedInputFile(file=image_data, filename='image.png')

                        await bot.send_photo(chat_id=sub.user, photo=image, caption=message_text, reply_markup=offer_markup(offer["link"]), parse_mode='html')
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)

    except Exception as e:
        print(f'Error in {sub.id}: {e}')
