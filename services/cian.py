import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from retrying import retry
from bot import start_bot, bot
import time
import re
from helpers.seleniumHelper import get_uc_driver
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs

load_dotenv()


async def search_cian(params):
    base_url = 'https://www.cian.ru/cat.php'

    parsed_url = urlparse(base_url)
    print(params)
    new_query = urlencode(params, encoding='utf-8')

    print(new_query)

    url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_query,
        parsed_url.fragment
    ))

    driver = get_uc_driver()
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        });
        '''})
    print(url)
    driver.get(url)
    time.sleep(3)


async def check_sub_cian(sub):
    items = await search_cian(sub.params)
    print(items)
