import os
import time
import datetime

from db_operations import get_all_users, update_db
from bot_notificator import send_message
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# if os.path.exists(dotenv_path):
#     load_dotenv(dotenv_path)

# Working 28.08.2024


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


def load_into_window(code, number):
    window = driver.find_element(By.NAME, 'realTrafficVUTemplate')
    window.clear()
    window.send_keys(code)  # Загружаем код в окно

    driver.find_element(By.XPATH, '//*[@id="findTrafficForm"]/td/table/tbody/tr[2]/td[2]/label[1]').click()
    driver.find_element(By.XPATH, '//*[@id="findTrafficForm"]/td/table/tbody/tr[3]/td[2]/a/img').click()  # Лупа

    driver.find_element(By.ID, 'checkbox-all').click()

    driver.find_element(By.XPATH, '//*[@id="findTrafficForm"]/td/table/tbody/tr[2]/td[2]/label[2]').click()
    driver.find_element(By.XPATH, '//*[@id="findTrafficForm"]/td/table/tbody/tr[3]/td[2]/a/img').click()  # Лупа

    driver.find_element(By.ID, 'checkbox-all').click()
    print(f'Добавлен элемент {number}){code}')


def load_codes(codelist):
    if len(codelist) == 0:
        print("Товаров, подлежащих инвентаризации не найдено")
        return
    counter = 0
    open_inventory_window()

    for code in codelist:
        counter += 1
        load_into_window(code, counter)
        if counter == 100:
            print('Журнал переполнен. Подтверждаем заявку и отправляем информацию...')
            try:
                approve_and_send()
            except:
                print("Не удалось подтвердить заявку...")
            open_inventory_window()
            counter = 0
    if counter != 0:
        approve_and_send()


def approve_and_send():
    driver.find_element(By.XPATH, '//*[@id="submitButton"]/span').click()
    driver.find_element(By.XPATH, '//*[@id="formButton"]/span').click()


def format_date(date):
    if "-" in date:
        date = date.split("-")[1].strip()
    if ":" in date:
        date = date.split(":")[0].strip()
    return date


def create_list_codes(df):
    def check_date(row):
        try:
            arrival = datetime.datetime.strptime(row[1], '%d.%m.%Y')
            expiry = datetime.datetime.strptime(row[2], '%d.%m.%Y')
        except:
            print("Произошла ошибка при работе с датой. Объект: ", row)
            return False
        today = datetime.datetime.now()
        two_months_ago = (today - datetime.timedelta(days=60))
        if (expiry <= today) or (arrival <= two_months_ago):
            return True
        return False

    result = []
    for row in df.itertuples(index=False, name='products'):
        if check_date(row):
            print(f"Добавлена запись {row[0]}; arrival: {row[1]}; expiry: {row[2]}")
            result.append(row[0])
    return result

def load_page():
    try:
        page_to_print = pd.read_html(driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML"))
        return page_to_print
    except:
        return None

if not os.path.exists("my_database.db"):
    print("configuration needed")
    update_db()

for user in get_all_users():
    objects_amount = user['objects_amount']
    # Driver settings
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    # options.add_argument("--headless=new")  # Interact with browser without any interface
    options.add_argument("--disable-blink-features=AutomationControlled")  # Disable web-driver mode
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                         " Chrome/96.0.4664.110 Safari/537.36")
    options.add_argument("--window-size=1920,1080")
    url = "https://mercury.vetrf.ru/hs"
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(50)

    pd.set_option('display.max_rows', None)
    try:
        driver.get(url)
        print("Для продолжения работы программы нужно войти вручную. Как только будет обнаружена страница с выбором ХС, программа продолжит работу")
        for current_object in range(2, int(objects_amount) + 2):
            print(f"Жду, когда появится элемент с номером {current_object}")
            WebDriverWait(driver, 200).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="body"]/form/div/div[1]/div/label[{current_object}]'))).click() # Выбираем объект учёта
            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[3]/form/div/div[2]/button[1]/span").click()  # Подтверждаем выбор
            driver.get("https://mercury.vetrf.ru/hs/operatorui?_action=listRealTrafficVU&stateMenu=2&pageList=1&all=true&preview=true") # Журнал продукции
            driver.find_element(By.XPATH, '//*[@id="body"]/table/tbody/tr/td[1]/ul/li/ul/li[3]/a').click()  # Неоформленные
            driver.find_element(By.XPATH, '/html/body/div[1]/div/div[3]/h3/span[1]').click()  # Нажимаем на i
            amount = driver.find_element(By.XPATH, '//*[@id="totalSizeView"]').text.split(':')[-1].strip(")").strip()  # (Найдено: n)

            # Составление списка с граничными номерами страниц
            amount = (float(amount) / 100).__ceil__()
            pagelist = [0]
            pagelist.extend([i for i in range(9, amount, 9)])
            pagelist.append((pagelist[-1] + amount % 9) if amount >= 9 else amount % 9)
            print(f"pagelist:{pagelist}")
            current_pages_idx = 0
            data = pd.DataFrame()

            driver.find_element(By.NAME, 'rows').click()  # Выбор менюшки
            driver.find_element(By.XPATH, '//*[@id="pageNavBlock"]/div[2]/select/option[6]').click()  # Выбор пункта меню 100
            while (current_pages_idx + 1) < len(pagelist):
                print(f"pages: {pagelist[current_pages_idx]}-{pagelist[current_pages_idx + 1]}")
                driver.find_element(By.XPATH, '//*[@id="printSettingsFormTop"]').click()  # Печать
                driver.find_element(By.XPATH, '//*[@id="printScopeLayout"]/td[2]/div/label[3]').click()  # Страница:
                pages = driver.find_element(By.XPATH,
                                            '//*[@id="printScopeLayout"]/td[2]/div/input')  # Форма ввода числа страниц
                pages.send_keys(f"{pagelist[current_pages_idx]}-{pagelist[current_pages_idx + 1]}")
                driver.find_element(By.XPATH, '//*[@id="printSchemaSelect"]').click()  # Селектор наборов полей
                driver.find_element(By.XPATH, '//*[@id="printSchemaSelect"]/option[2]').click()  # Выбираем main
                driver.find_element(By.XPATH,
                                    '//*[@id="printSettingsForm"]/table/tbody/tr[4]/td/div/button[1]').click()  # Печать
                main_handle = driver.current_window_handle
                driver.switch_to.window(driver.window_handles[1])
                page_to_print = None
                while page_to_print is None:
                    time.sleep(1)
                    page_to_print = load_page()
                page_to_print = page_to_print[-1]
                page_to_print = page_to_print.drop(page_to_print.columns[[0]], axis=1)
                data = pd.concat([data, page_to_print], ignore_index=True)
                driver.close()
                driver.switch_to.window(main_handle)
                current_pages_idx += 1
            data['Годен до'] = data['Годен до'].apply(format_date)
            # print(data)
            codes = create_list_codes(data)
            print("Количество записей, удовлетворяющих критериям: " + str(len(codes)))
            send_message(message=f"Записей подлежащих инвентаризации: {len(codes)}", chat_id=user['telegram_id'])
            load_codes(codes)
            # time.sleep(1000000)
            # for i in range(2):
            #     print(f"Программа автоматически завершит свою работу через {20 - (i * 10)} секунд")
            #     time.sleep(10)
            send_message(message="Программа успешно завершила работу", chat_id=user['telegram_id'])
            driver.get("https://mercury.vetrf.ru/hs/operatorui?_action=changeServicedEnterprise") # Смена предприятия
    except Exception as ex:
        print(ex)
        send_message(message="Произошла ошибка при инвентаризации! Уже разбираемся..", chat_id=user['telegram_id'])
        send_message(message=f"Произошла ошибка при инвентаризации пользователем {user['login']}\n" + str(ex),
                     chat_id="954179273")
    finally:
        driver.close()
        driver.quit()
