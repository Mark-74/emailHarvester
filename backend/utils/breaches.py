import requests, time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

def is_breached(domain: str) -> bool:
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    with webdriver.Firefox(options=options) as driver:
        driver.get(f'https://www.breachsense.com/check-your-exposure/?domain={domain}')
        time.sleep(3)
        page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    return soup.find('h2').text == 'Data Breach Detected'
