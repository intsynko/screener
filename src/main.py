import json
import pathlib
from json import JSONDecodeError

import pyautogui

from printers.console import ConsolePrinter
from printers.tg_printer import TelegramPrinter
from printers.vk_printer import VkPrinter
from printers.window import WindowPrinter
from processor import Processor
from printers.base_printer import Level
from telegram_connector import TelegramConnector
from vk_connector import VkConnector


def init_processor():
    try:
        config = json.load(open(str(pathlib.Path() / 'config.json'), 'r'))
    except FileNotFoundError:
        raise ValueError('Не вижу файл конфига')
    except JSONDecodeError:
        raise ValueError('Ошибка в настройки конфиг файла')
    else:
        try:
            messenger = config.get('messenger', 'telegram')

            tg_connector = TelegramConnector(config)

            if messenger == 'vk':
                messenger_connector = VkConnector(config)
                printer_key = 'vk'
            else:
                messenger_connector = tg_connector
                printer_key = config.get('printer', 'telegram')

            printer = {
                'console': ConsolePrinter,
                'telegram': TelegramPrinter,
                'vk': VkPrinter,
                'window': WindowPrinter,
            }[printer_key](
                config,
                level=Level.INFO,
                tg_connector=tg_connector,
                vk_connector=messenger_connector if messenger == 'vk' else None,
            )
            return Processor(config, printer, tg_connector, messenger_connector)
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
