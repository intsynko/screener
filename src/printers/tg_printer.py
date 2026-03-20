from printers.base_printer import BasePrinter
from telegram_connector import TelegramConnector


class TelegramPrinter(BasePrinter):

    def __init__(self, config, level, **kwargs):
        self.tg_connector = TelegramConnector(config)
        super().__init__(config, level)

    def _print(self, msg, level):
        self.tg_connector.send_message(msg)
