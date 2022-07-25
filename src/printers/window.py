import pyautogui

from printers.base_printer import BasePrinter, Level


class WindowPrinter(BasePrinter):

    def __init__(self, config, level, **kwargs):
        super().__init__(config, level)

    def _print(self, msg, level):
        if level == Level.ERROR:
            title = 'Ошибка'
        else:
            title = ''
        pyautogui.alert(text=msg, title=title, button='OK')
