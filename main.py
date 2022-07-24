"""
Скрипт, отсылающий скрин экрана в чат телеграма через бота.
Скрипт использует конфиг в виде json файла со след. полями:
max_time - (int) максимальное время работы скрипта в минутах
bot_token - (str) токен бота (в формате 0000000:aaaaaaa...)
chat_id - (str) id чата в телеграмме (меожет быть отрицательным)
exit_btn_code - (int) - код клавишы выхода, изначально TAB 9 (https://stackoverflow.com/questions/31363860/how-do-i-get-the-name-of-a-key-in-pywin32-giving-its-keycode)
"""
import io
import json
import pathlib
import time

import pyautogui
import requests
import win32api

from printers.console import ConsolePrinter

started = time.time()

try:
    config = json.load(open(str(pathlib.Path() / 'config.json'), 'r'))

    max_time = int(config["max_time"])  # максимальное время работы скрипта в минутах
    bot_token = config["bot_token"]  # токен бота
    chat_id = int(config["chat_id"])  # id чата
    push_message_btn = int(config.get("push_message_btn", 4))  # по дефолту колесико мыши
    exit_btn_code = int(config.get("exit_btn_code", 9))  # по дефолту TAB
except:
    pyautogui.alert(text='Ошибка в настройки конфиг файла', title='Ошибка', button='OK, поправлю')
    exit(0)


printer = ConsolePrinter(config)
state_left = win32api.GetKeyState(4)

while True:
    scroll_btn = win32api.GetKeyState(4)

    if scroll_btn != state_left:  # Button state changed
        state_left = scroll_btn
        if scroll_btn < 0:
            myScreenshot = pyautogui.screenshot()

            img_byte_arr = io.BytesIO()
            myScreenshot.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            files = {'photo': img_byte_arr}

            resp = requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendPhoto?chat_id={chat_id}", files=files)
            printer.print_msg(time.time() - started)
    # завершаем работу по истечению времени (/60 - переводим м минуты)
    if (time.time() - started) / 60 > max_time:
        printer.print_msg(f'завершилось время')
        break
    # так же завершение работы по нажатию клавишы выхода
    if win32api.GetKeyState(exit_btn_code) == 0:
        printer.print_msg(f'нажата клавиша #{exit_btn_code}')
        break
