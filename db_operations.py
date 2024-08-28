import sqlite3


def get_all_users() -> list:
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Users')
    users = cursor.fetchall()
    result = [{"login": user[1], "password": user[2], "telegram_id": user[3]} for user in users]
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
    telegram TEXT)
    ''')

    username = input('Enter username: ')
    password = input('Enter password: ')
    telegram = input('Enter telegram: ')

    cursor.execute('INSERT INTO Users (username, password, telegram) VALUES (?, ?, ?)', (username, password, telegram))
    connection.commit()
    connection.close()


# update_db()
