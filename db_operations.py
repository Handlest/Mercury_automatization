import sqlite3


def get_all_users() -> list:
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Users')
    users = cursor.fetchall()
    result = [{"login": user[1], "password": user[2], "object_index": user[3], "telegram_id": user[4]} for user in users]
    connection.close()
    return result


def delete_user(username: str):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Users')
    cursor.execute(f'DELETE FROM Users WHERE Username=?', (username,))
    connection.commit()
    connection.close()


def update_db():
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    object_index TEXT NOT NULL,
    telegram TEXT)
    ''')

    username = input('Введите логин: ')
    password = input('Введите пароль: ')
    telegram = input('Введите телеграм ID(можно оставить пустым и нажать enter): ')
    object_index = input('Введите номер объекта учёта (если он один, то цифру 2): ')

    cursor.execute('INSERT INTO Users (username, password, object_index, telegram) VALUES (?, ?, ?, ?)',
                   (username, password, object_index, telegram))
    connection.commit()
    connection.close()


# update_db()
