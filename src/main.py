import json
import pathlib
from json import JSONDecodeError

import pyautogui

from printers.console import ConsolePrinter
from processor import Processor
from src.printers.base_printer import Level
from telegram_connector import TelegramConnector


def init_processor():
    try:
        config = json.load(open(str(pathlib.Path() / 'config.json'), 'r'))
    except FileNotFoundError:
        raise ValueError('Не вижу файл конфига')
    except JSONDecodeError:
        raise ValueError('Ошибка в настройки конфиг файла')
    else:
        try:
            tg_connector = TelegramConnector(config)
            printer = ConsolePrinter(config, level=Level.INFO)
            return Processor(config, printer, tg_connector)
        except ValueError:
            raise


if __name__ == "__main__":
    try:
        processor = init_processor()
    except ValueError as ex:
        pyautogui.alert(text=str(ex), title='Ошибка', button='OK, поправлю')
        exit(0)
    else:
        processor.run_loop()
