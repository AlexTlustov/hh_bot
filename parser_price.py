import time
import datetime
from time import sleep
from bs4 import BeautifulSoup
from httpcore import TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import difflib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from database.db import get_all_user_products

# Получаем драйвер
def get_driver_engine(url, wait_time):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(url)
    except TimeoutException:
        print(f'Превышено время ожидания ответа страницы: {url}\nЗапрос будет отправлен повторно через 3 минуты.')
        driver.quit()
        sleep(wait_time)
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        return driver
    return driver

# Получаем информацию о продукте
def get_info_about_product(keyword):
    url = 'https://korzina.su/'
    product_list = []
    status = True
    count = 0
    while status:
        try:
            driver = get_driver_engine(url, 180)
            search_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.search_input"))
            )
            time.sleep(2)
            search_input.send_keys(keyword)
            search_input.send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.digi-product"))
            )
            time.sleep(2)
            products = driver.find_elements(By.CSS_SELECTOR, "div.digi-product")
            for product in products:
                product_meta = product.find_element(By.CSS_SELECTOR, "div.digi-product__meta")
                product_name = product_meta.find_element(By.CSS_SELECTOR, "a.digi-product__label").text
                product_footer = product.find_element(By.CSS_SELECTOR, "div.digi-product__footer")
                product_price_element = product_footer.find_element(By.CSS_SELECTOR, "span.digi-product-price-variant.digi-product-price-variant_actual")
                if product_price_element:
                    product_price = product_price_element.text
                    price_str = ''.join(char for char in product_price if char.isdigit() or char in ('.', '₽', ','))
                    price_str = price_str.replace("₽", "")
                    price_str = price_str.replace(",", ".")
                    product_price_float = float(price_str)
                    product_list.append({'name': product_name, 'price': product_price_float})
            status = False
            print('Данные товара успешно получены.')
        except:
            driver.quit()
            print('Данные товара не получены, отправляю повторный запрос.')
            count += 1
            if count > 5:
                status = False
                print('Данные товара не получены, отправлено слишком много запросов.')
            time.sleep(10)
            continue

    driver.quit()
    return product_list

# Получаем цену на товары
def get_price_for_product():
    time_start = datetime.datetime.now()
    product_dict_user = get_all_user_products()
    only_product_name = []
    data = []
    for element in product_dict_user:
        product = element['name']
        quantity = element['quantity']
        product_id = element['product_id']
        product_list = get_info_about_product(product)
        for x in product_list:
            name = x['name']
            only_product_name.append(name)
        close_matches = difflib.get_close_matches(product, only_product_name, cutoff=0.7)
        only_product_name.clear()
        if len(close_matches) == 0:
            similar = product_list[0]
            similar_name = similar['name']
            full_price = similar['price'] * quantity
            status_price = 'Цена получена.'
        else:
            similar_name = ''
            for object in product_list:
                try:
                    if object['name'] == close_matches[0]:
                        price = object['price']
                except:
                    if price is None:
                        status_price = 'Цена не найдена.'
            if float(price):          
                full_price = price * quantity
                status_price = 'Цена получена.'
            else:
                full_price = 0
                status_price = 'Цена не изменена.'
        data.append({'product_id': product_id, 'full_price': full_price, 'status': status_price, 'similar_name': similar_name})
        time.sleep(2)
    user_msg = 'Все цены обновлены.'
    time_finish = datetime.datetime.now()
    print(f'{user_msg} Время выполнения: {time_finish - time_start}')
    return data


