from printers.base_printer import BasePrinter, Level
from vk_connector import VkConnector


class VkPrinter(BasePrinter):

    def __init__(self, config, level: Level, **kwargs):
        super().__init__(config, level)
        self._vk_connector = VkConnector(config)

    def _print(self, msg, level):
        self._vk_connector.send_message(msg)

    def send_pic(self, img_byte_arr):
        self._vk_connector.send_pic(img_byte_arr)
