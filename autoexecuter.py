import datetime
import os
import random
with open("next_exec_time.txt") as file:
    tmp = datetime.datetime.now()
    current_time = f'{tmp.hour}:{tmp.minute}'
    current_date = f'{tmp.year}-{tmp.month}-{tmp.day}'
    file_time = file.readline().strip()
    file_date = file.readline().strip()

    print(file_date, current_date, file_date == current_date)
    print(file_time, current_time, file_time == current_time)

    if current_date == file_date and current_time == file_time:
        os.system("venv/bin/python3.10 main.py")
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        file.close()
        file = open("next_exec_time.txt", "w")
        file.writelines(f"{random.randint(17, 23)}:{random.randint(10, 59)}\n")
        file.writelines(f"{tomorrow.year}-{tomorrow.month}-{tomorrow.day}\n")
