from typing import List, Dict

import requests


class TelegramConnectorException(ValueError):
    pass


class TelegramConnector:
    url = "https://api.telegram.org/bot"

    def __init__(self, config):
        try:
            self.bot_token = config["bot_token"]  # токен бота
            self.chat_id = int(config["chat_id"])  # id чата
            self.compression = bool(config.get("compression", True))
        except KeyError:
            raise TelegramConnectorException("bot_token и chat_id обязательные параметры конфига")
        except ValueError:
            raise TelegramConnectorException("ошибка заполнения chat_id")

        self._offset = 1

    def send_message(self, msg):
        self._send_request(
            url=f"{self.url}{self.bot_token}/sendMessage?chat_id={self.chat_id}",
            json={
                'text': msg,
                'disable_web_page_preview': True
            }
        )

    def send_pic(self, img_byte_arr):
        if self.compression:
            files = {'photo': img_byte_arr}
            self._send_request(
                url=f"{self.url}{self.bot_token}/sendPhoto?chat_id={self.chat_id}",
                files=files
            )
        else:
            files = {'document': ('screen.png', img_byte_arr)}
            self._send_request(
                url=f"{self.url}{self.bot_token}/sendDocument?chat_id={self.chat_id}",
                files=files
            )

    def set_commands(self, commands: List[Dict]):
        self._send_request(
            url=f"{self.url}{self.bot_token}/setMyCommands",
            json={
                "commands": commands
            }
        )

    def get_updates(self):
        params = {}
        if self._offset:
            params["offset"] = self._offset
        resp = self._send_request(
            url=f"{self.url}{self.bot_token}/getUpdates",
            params=params,
        )
        data = resp.json()["result"]
        # если офсет уже был, значит первое сообщение мы уже читали
        if self._offset > 1:
            data = data[1:]
        else:
            # если это первый запрос, то оставляем последнее сообщение, чтобы взять с него offset
            self._offset = data[-1]["update_id"]
            data = []
        # если есть новые сообщения - то двигаем оффсет
        if len(data) > 0:
            self._offset = data[-1]["update_id"]
        return data

    def get_commands(self) -> List[str]:
        messages = self.get_updates()
        commands = []
        for message in messages:
            is_cmd = next((True for ent in message.get("message", {}).get("entities", {}) if ent.get("type") == "bot_command"), False)
            if is_cmd:
                commands.append(message["message"]["text"])
        return commands

    def _send_request(self, **kwargs):
        resp = requests.post(
            **kwargs
        )
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            raise TelegramConnectorException(f'Нерпавильно настроена связь с телеграмм: {ex}')
        return resp
