import datetime
import os
from io import BytesIO

import requests
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from retrying import retry
from aiogram.types import InputFile, BufferedInputFile
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bot import start_bot, bot
import time
import re

from config.database.notification_queries import find_notification, save_notification
from helpers.seleniumHelper import get_uc_driver
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs

from helpers.textHelper import truncate_text
from helpers.urlHelper import add_params_url
from loader import logger
from markups.offer_markup import offer_markup

load_dotenv()


async def search_cian(params):
    base_url = 'https://www.cian.ru/cat.php'

    url = add_params_url(base_url, params)

    driver = get_uc_driver(headless=False)
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
        logger.error(f'Error open page: {str(e)}')

    time.sleep(3)

    try:
        # Ждем появления модального окна с aria-modal="true"
        modal = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@aria-modal="true" and @role="dialog"]'))
        )

        # Находим кнопку-крестик для закрытия модального окна
        close_button = modal.find_element(By.XPATH, './/div[@role="button" and @aria-label="Закрыть"]')

        # Кликаем на кнопку-крестик
        close_button.click()

    except Exception as e:
        logger.error("Error interacting with modal or closing the modal: %s", str(e))
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        driver.save_screenshot(os.path.join("results", f"error_{timestamp}.png"))

    # Ожидаем, пока появится элемент с уведомлением о куки
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@data-name="CookiesNotification"]//button'))
        )
        cookie_button.click()
    except Exception as e:
        logger.warning("Cookie notification could not be closed: %s", str(e))
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        driver.save_screenshot(os.path.join("results", f"error_{timestamp}.png"))

    wait = WebDriverWait(driver, 10)
    pagination_section = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-name="PaginationSection"]')))

    # Поиск всех элементов страниц внутри ul
    pages = pagination_section.find_elements(By.XPATH, './/ul/li')
    logger.debug(f"Pages: {pages}")
    # Получаем количество страниц
    total_pages = len(pages) or 1
    logger.debug(f"Total pages: {total_pages}")

    try:
        result = []
        for i in range(total_pages):
            logger.debug(f"Page: {i + 1}")
            try:
                offers_wrapper = wait.until(
                    EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"_93444fe79c--wrapper--W0WqH") and not(@data-name="Suggestions")]')))
                offers = offers_wrapper.find_elements(By.XPATH, './/article')
                # offers = driver.find_elements(By.XPATH, '//div[contains(@class,"_93444fe79c--wrapper--W0WqH") and not(@data-name="Suggestions")]/div')
                logger.debug(f"Total offers on page: {len(offers)}")

                for offer in offers:
                    try:
                        title = offer.find_element(By.XPATH, './/span[@data-mark="OfferTitle"]/span').text
                        logger.debug(title)
                        location = offer.find_element(By.XPATH, './/div[@class="_93444fe79c--labels--L8WyJ"]').text
                        price = offer.find_element(By.XPATH, './/span[@data-mark="MainPrice"]/span').text
                        price_info = offer.find_element(By.XPATH, './/p[@data-mark="PriceInfo"]').text
                        link = offer.find_element(By.TAG_NAME, 'a').get_attribute('href')
                        description = offer.find_element(By.XPATH, './/div[contains(@data-name,"Description")]/p').text
                        author = offer.find_element(By.XPATH, './/div[contains(@data-name,"BrandingLevelWrapper")]/div/div[contains(@class,"content")]/div/div/span').text

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
                        logger.error(f"Error in offer: {e}")

            except Exception as e:
                logger.error(f'Error get cian offers on page {i}: {e}')

            if i + 1 < total_pages:
                pages = pagination_section.find_elements(By.XPATH, './/ul/li')
                next_page = pages[i + 1]
                next_page_link = next_page.find_element(By.XPATH, ".//a")
                next_page_link.click()
                time.sleep(3)
                continue
        driver.quit()
        logger.debug(f"Result: {result}")
        logger.debug(f"Total result: {len(result)}")
        return result
    except Exception as e:
        raise


async def check_sub_cian(sub):
    try:
        offers = await search_cian(sub.params)
        notys = []

        if offers:
            try:
                for offer in offers:
                    try:
                        if not await find_notification(link=offer["link"], site='cian'):
                            await save_notification(title=offer["title"], link=offer["link"], user=sub.user, site='cian')
                            message_text = f'{offer["title"]} - {offer["price"]}\n{offer["price_info"]}\n{offer["location"]}\nАвтор: {offer["author"]}\n\n<i>{offer["description"]}</i>'

                            notys.append({
                                "image_url": offer["image_url"],
                                "link": offer["link"],
                                "message_text": message_text
                            })

                    except Exception as e:
                        logger.error(e)

            except Exception as e:
                logger.error(e)

        return notys
    except Exception as e:
        logger.error(f'Error in sub {sub.id}: {e}')
