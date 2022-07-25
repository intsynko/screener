import requests


class TelegramConnectorException(ValueError):
    pass


class TelegramConnector:

    def __init__(self, config):
        try:
            self.bot_token = config["bot_token"]  # токен бота
            self.chat_id = int(config["chat_id"])  # id чата
        except KeyError:
            raise TelegramConnectorException("bot_token и chat_id обязательные параметры конфига")
        except ValueError:
            raise TelegramConnectorException("ошибка заполнения chat_id")

    def send_pic(self, img_byte_arr):
        files = {'photo': img_byte_arr}
        resp = requests.post(
            f"https://api.telegram.org/bot{self.bot_token}/sendPhoto?chat_id={self.chat_id}",
            files=files
        )
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            raise TelegramConnectorException(f'Нерпавильно настроена связь с телеграмм: {ex}')
