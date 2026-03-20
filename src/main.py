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
            screener = config.get('screener', 'telegram')
            if screener == 'vk':
                screener_connector = VkConnector(config)
            elif screener == 'telegram':
                screener_connector = TelegramConnector(config)
            else:
                raise NotImplementedError("Неизвестный screener")

            printer = {
                'console': ConsolePrinter,
                'telegram': TelegramPrinter,
                'vk': VkPrinter,
                'window': WindowPrinter,
            }[config.get('printer', 'telegram')](
                config,
                level=Level.INFO,
            )
            return Processor(config, printer, screener_connector)
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
