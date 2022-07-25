import requests


class TelegramConnectorException(ValueError):
    pass


class TelegramConnector:
    url = "https://api.telegram.org/bot"

    def __init__(self, config):
        try:
            self.bot_token = config["bot_token"]  # токен бота
            self.chat_id = int(config["chat_id"])  # id чата
        except KeyError:
            raise TelegramConnectorException("bot_token и chat_id обязательные параметры конфига")
        except ValueError:
            raise TelegramConnectorException("ошибка заполнения chat_id")

    def send_message(self, msg):
        self._send_request(
            url=f"{self.url}{self.bot_token}/sendMessage?chat_id={self.chat_id}",
            json={
                'text': msg,
                'disable_web_page_preview': True
            }
        )

    def send_pic(self, img_byte_arr):
        files = {'photo': img_byte_arr}
        self._send_request(
            url=f"{self.url}{self.bot_token}/sendPhoto?chat_id={self.chat_id}",
            files=files
        )

    def _send_request(self, **kwargs):
        resp = requests.post(
            **kwargs
        )
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            raise TelegramConnectorException(f'Нерпавильно настроена связь с телеграмм: {ex}')
