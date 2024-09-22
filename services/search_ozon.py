import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from retrying import retry
import time
import re

load_dotenv()


def search_ozon(query, max_price):
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"user-agent={os.getenv('USER_AGENT')}")
    options.add_argument("--headless")  # не открывать окно браузера

    # Инициализация драйвера с использованием webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    # driver = webdriver.Chrome()
    driver.get('https://www.ozon.ru/')
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
        min_price_input = driver.find_element(By.XPATH, '//div[@filter-key="currency_price"]//p[contains(text(), "от")]/preceding-sibling::input')
        min_price_input.clear()
        min_price_input.send_keys('30000')
        print("Минимальная цена введена успешно")

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def enter_max_price():
        max_price_input = driver.find_element(By.XPATH, '//div[@filter-key="currency_price"]//p[contains(text(), "до")]/preceding-sibling::input')
        max_price_input.clear()
        max_price_input.send_keys(str(max_price))
        max_price_input.send_keys(Keys.RETURN)
        print("Максимальная цена введена успешно")

    try:
        enter_min_price()
    except Exception as e:
        print("Ошибка при вводе минимальной цены после 5 попыток:", e)

    try:
        enter_max_price()
    except Exception as e:
        print("Ошибка при вводе максимальной цены после 5 попыток:", e)

    time.sleep(3)  # Ждем обновления результатов

    # Сбор информации о товарах
    products = driver.find_elements(By.CLASS_NAME, 'q1j_23')  # Найдите правильный селектор для товаров
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