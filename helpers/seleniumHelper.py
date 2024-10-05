from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
import os
from dotenv import load_dotenv

load_dotenv()


def get_options():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"user-agent={os.getenv('USER_AGENT')}")
    options.add_argument("--disable-webrtc")
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option('useAutomationExtension', False)
    # options.add_argument("--headless")  # не открывать окно браузера

    return options


def get_driver():
    # Инициализация драйвера с использованием webdriver-manager
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=get_options())


def get_uc_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"user-agent={os.getenv('USER_AGENT')}")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-webrtc")
    options.add_argument('--window-size=1920,1080')
    # options.add_argument("--headless")  # не открывать окно браузера
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option('useAutomationExtension', False)
    return uc.Chrome(use_subprocess=False, options=options)
