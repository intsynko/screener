import io
import time

import pyautogui
import win32api

from printers.base_printer import Level
from telegram_connector import TelegramConnectorException


class Processor:

    def __init__(self, config, printer, tg_connector):
        self.max_time = int(config.get("max_time", 60))
        self.push_message_btn = int(config.get("push_message_btn", 4))
        self.exit_btn_code = int(config.get("exit_btn_code", 9))

        self.printer = printer
        self.tg_connector = tg_connector

        self._started = None
        self._5_minute_notified = False

    def run_loop(self):
        self.printer.print_msg('started')
        self._started = time.time()

        state_left = win32api.GetKeyState(self.push_message_btn)
        while True:
            scroll_btn = win32api.GetKeyState(self.push_message_btn)

            if scroll_btn != state_left:  # Button state changed
                state_left = scroll_btn
                if scroll_btn < 0:
                    screenshot = self.make_screenshot()
                    try:
                        self.tg_connector.send_pic(screenshot)
                    except TelegramConnectorException as ex:
                        self.printer.print_msg(ex, level=Level.ERROR)
                    else:
                        self.printer.print_msg(time.time() - self._started, level=Level.DEBUG)
            self.notify()
            if self.check_exit():
                break

    def make_screenshot(self):
        myScreenshot = pyautogui.screenshot()
        img_byte_arr = io.BytesIO()
        myScreenshot.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr

    @property
    def work_time(self):
        # (/60 - переводим м минуты)
        return (time.time() - self._started) / 60

    def notify(self):
        # за 5 минут до конца сигнализируем о скором заверщении
        if self.work_time == self.max_time - 5 and not self._5_minute_notified:
            self.printer.print_msg(f'5 минут до завершения')
            self._5_minute_notified = True

    def check_exit(self) -> bool:
        # завершаем работу по истечению времени (/60 - переводим м минуты)
        if self.work_time > self.max_time:
            self.printer.print_msg(f'завершилось время')
            return True

        # так же завершение работы по нажатию клавишы выхода
        if win32api.GetKeyState(self.exit_btn_code) < 0:
            self.printer.print_msg(f'нажата клавиша #{self.exit_btn_code}')
            return True

        return False
