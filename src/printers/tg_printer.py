from printers.base_printer import BasePrinter
from telegram_connector import TelegramConnector


class TelegramPrinter(BasePrinter):

    def __init__(self, config, level, tg_connector: TelegramConnector, **kwargs):
        self.tg_connector = tg_connector
        super().__init__(config, level)

    def _print(self, msg, level):
        self.tg_connector.send_message(msg)
