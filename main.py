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

config = json.load(open(str(pathlib.Path()/'config.json'), 'r'))
started = time.time()
max_time = config["max_time"]  # максимальное время работы скрипта в минутах
bot_token = config["bot_token"]  # токен бота
chat_id = config["chat_id"]  # id чата
exit_btn_code = config["exit_btn_code"]


state_left = win32api.GetKeyState(0x01)
state_right = win32api.GetKeyState(0x02)

while True:
    scroll_btn = win32api.GetKeyState(0x04)

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
            print(time.time() - started)
    # завершаем работу по истечению времени (/60 - переводим м минуты)
    if (time.time() - started) / 60 > max_time:
        print(f'завершилось время')
        break
    # так же завершение работы по нажатию клавишы TAB
    if win32api.GetAsyncKeyState(9):
        print(f'нажата клавиша TAB')
        break
