import time
import datetime
from login_data import password, login
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

product_codes = []
check_next = True
# working 18.08.2023

options = webdriver.ChromeOptions()
options.headless = False  # Interact with browser without any interface
options.add_argument("--disable-blink-features=AutomationControlled")  # Disable web-driver mode
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                     " Chrome/96.0.4664.110 Safari/537.36")
url = "https://mercury.vetrf.ru/hs"
driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
driver.implicitly_wait(10)


def in_date_range(date):
    global check_next
    today = datetime.datetime.now()
    two_months_ago = (today - datetime.timedelta(days=45)).toordinal()
    curr_date = datetime.datetime.strptime(date, '%d.%m.%Y').toordinal()
    today = today.toordinal()
    if two_months_ago >= curr_date:
        check_next = False
    return two_months_ago <= curr_date <= today


def load_into_window(current, window, number):
    window.clear()
    window.send_keys(current.split()[1])  # Загружаем код в окно

    driver.find_element(By.XPATH, '//*[@id="findTrafficForm"]/td/table/tbody/tr[2]/td[2]/label[1]').click()
    driver.find_element(By.XPATH, '//*[@id="findTrafficForm"]/td/table/tbody/tr[3]/td[2]/a/img').click()  # Лупа

    driver.find_element(By.ID, 'checkbox-all').click()

    driver.find_element(By.XPATH, '//*[@id="findTrafficForm"]/td/table/tbody/tr[2]/td[2]/label[2]').click()
    driver.find_element(By.XPATH, '//*[@id="findTrafficForm"]/td/table/tbody/tr[3]/td[2]/a/img').click()  # Лупа

    driver.find_element(By.ID, 'checkbox-all').click()
    print(f'Добавлен элемент {number}){current}')

def load_codes():
    counter = 0
    added_codes = []
    open_inventory_window()
    window_to_load = driver.find_element(By.NAME, 'realTrafficVUTemplate')

    for i in range(len(product_codes)):
        if counter != 100:
            if in_date_range(product_codes[i].split()[0]):
                counter += 1
                load_into_window(product_codes[i], window_to_load, counter)
                added_codes.append(product_codes[i])
        else:
            print('Журнал переполнен. Подтверждаем заявку и отправляем информацию...')
            approve_and_send()
            if in_date_range(product_codes[i].split()[0]):
                counter = 1
                open_inventory_window()
                window_to_load = driver.find_element(By.NAME, 'realTrafficVUTemplate')
                print(product_codes[i])
                print(window_to_load)
                load_into_window(product_codes[i], window_to_load, counter)
                added_codes.append(product_codes[i])


def open_inventory_window():
    driver.get("https://mercury.vetrf.ru/hs/operatorui?_action=listInventory&stateMenu=0&all=true")  # Инвентаризация
    driver.find_element(By.XPATH, '//*[@id="body"]/form/div[1]/ul/li[4]/span').click()
    upper_window = Select(driver.find_element(By.XPATH, '//*[@id="inventory-cause"]'))  # Верхнее окошко
    upper_window.select_by_visible_text(
        "Сопоставление фактически имеющейся продукции с учетными данными компонента Меркурий")
    lower_window = Select(driver.find_element(By.XPATH, '//*[@id="inventory-reason-from-reference-select"]'))
    lower_window.select_by_visible_text(
        "Сопоставление фактически имеющейся продукции с учетными данными (выявление отклонений).")

    driver.find_element(By.XPATH, '//*[@id="btn-submit"]/span').click()

    driver.find_element(By.XPATH, '//*[@id="body"]/form/table/tbody/tr[3]/td/h4/a').click()  # Добавить
    driver.find_element(By.XPATH,
                        '//*[@id="realTrafficFindForm"]/table/tbody/tr[1]/td/table/tbody/tr/td[2]/label[3]').click()  # Удаление


def approve_and_send():
    driver.find_element(By.XPATH, '//*[@id="submitButton"]/span').click()
    driver.find_element(By.XPATH, '//*[@id="formButton"]/span').click()


def get_codes():
    dates = driver.find_elements(By.XPATH, '//*[@id="listContent"]/table/tbody/tr/td[7]')
    ids = driver.find_elements(By.XPATH, '//*[@id="listContent"]/table/tbody/tr/td[2]')
    for q in range(1, len(dates)):
        date = dates[q].text.strip()
        if ":" in date:
            date = date.split(":")[0].strip()
        if "-" in date:
            date = date.split("-")[0].strip()
        if not in_date_range(date):
            continue
        product_codes.append(f'{date} {ids[q].text}')

try:
    driver.get(url)
    username_input = driver.find_element(By.ID, "username")  # Выбираем окно "имя пользователя"
    username_input.send_keys(login)  # Вводим имя пользователя
    password_input = driver.find_element(By.ID, "password")  # Выбираем окно "пароль"
    password_input.send_keys(password)  # Вводим пароль пользователя
    driver.find_element(By.CLASS_NAME, "login-btn").click()  # Нажимаем на кнопку "войти"
    driver.find_element(By.XPATH, '//*[@id="body"]/form/table/tbody/tr[1]/td/div/label[2]').click()  # Выбираем объект учёта
    driver.find_element(By.CLASS_NAME, "positive").click()  # Подтверждаем выбор
    driver.get("https://mercury.vetrf.ru/hs/operatorui?_action=listVetDocument&pageList=1&all=true&request=true&preview=true")  # Ветеринарные документы
    driver.find_element(By.XPATH, '//*[@id="body"]/table/tbody/tr/td[3]/ul/li/ul/li[2]/a').click()  # Погашенные
    driver.find_element(By.NAME, 'rows').click()  # Выбор менюшки
    driver.find_element(By.XPATH, '//*[@id="pageNavBlock"]/div[2]/select/option[6]').click()  # Выбор пункта меню 100
    # Далее идёт сбор дат и кодов с указанного числа страниц

    while len(driver.find_elements(By.LINK_TEXT, 'Следующая')) > 0 and check_next:
        get_codes()
        driver.find_element(By.LINK_TEXT, 'Следующая').click()  # Следующая
    get_codes()
    print(f"Количество найденных элементов: {len(product_codes)}")
    load_codes()
    print("Программа завершила свою работу. Сохраняем журнал..\n")

    if driver.find_element(By.XPATH, '//*[@id="submitButton"]/span').is_displayed() and\
            driver.find_element(By.XPATH, '//*[@id="submitButton"]/span').is_enabled():
        approve_and_send()
    else:
        print("Неинвентаризованных товаров в списке больше не найдено..")
        driver.find_element(By.XPATH, '//*[@id="realTrafficFindForm"]/table/tbody/tr[3]/td/button[2]/span').click()
        driver.find_element(By.XPATH, '//*[@id="body"]/form/table/tbody/tr[4]/td/button[2]/span').click()
        driver.find_element(By.XPATH, '//*[@id="confirm-dialog-btn-ok"]/span').click()

    for i in range(2):
        print(check_next)
        print(f"Программа автоматически завершит свою работу через {20 - (i*10)} секунд")
        time.sleep(10)

except Exception as ex:
    print(ex)
    time.sleep(20)
finally:
    driver.close()
    driver.quit()