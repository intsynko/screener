import time
from typing import List


class CommandsExecutor:

    def __init__(self, tg_connector, printer, processor, config):
        self.tg_connector = tg_connector
        self.printer = printer
        self.processor = processor

        self.commands_pull_delay = int(config.get("pull_delay", 3))
        self.commands_enabled = bool(config.get("enabled", True))
        self.cmd_shutdown_enabled = bool(config.get("shutdown_enabled", True))

    def set_commands(self):
        if not self.commands_enabled:
            return
        self.tg_connector.set_commands([
            {
                "command": "check_rest_time",
                "description": "Узнать оставшееся время работы",
            },
            {
                "command": "renew_for_30_minute",
                "description": "Продлить время работы на 30 минут",
            },
            {
                "command": "renew_for_1_hour",
                "description": "Продлить время работы на 1 час",
            },
            {
                "command": "shutdown",
                "description": "Завершить",
            },
            {
                "command": "accept_shutdown",
                "description": "Подтвердить завершение",
            }
        ])

    def check_commands(self):
        if not self.commands_enabled:
            return
        if hasattr(self, '_last_cmd_update'):
            if time.time() - self._last_cmd_update < self.commands_pull_delay:
                return
        self._last_cmd_update = time.time()
        commands = self.tg_connector.get_commands()
        self.commands_process(commands)

    def commands_process(self, commands: List[str]):
        for cmd in commands:
            cmd = cmd[1:].split('@')[0]
            processor = getattr(self, cmd, None)
            if callable(processor):
                processor()

    def check_rest_time(self):
        rest = self.processor.max_time - self.processor.work_time
        self.printer.print_msg(f"Осталось {round(rest)} минут")

    def renew_for_30_minute(self):
        self.processor.max_time += 30
        self.check_rest_time()

    def renew_for_1_hour(self):
        self.processor.max_time += 60
        self.check_rest_time()

    def shutdown(self):
        if not self.cmd_shutdown_enabled:
            self.printer.print_msg(f"Выключение запрещено настройками")
            return
        self._shut_down_inited_time = time.time()
        self.printer.print_msg(f"Подтверите завершение в течении 15 секунд")

    def accept_shutdown(self):
        if not hasattr(self, '_shut_down_inited_time'):
            self.printer.print_msg(f"Снача нужно инициализировать /shutdown")
            return
        if time.time() - self._shut_down_inited_time > 15:
            self.printer.print_msg(f"Вышло время подтверждения")
        else:
            self.processor.max_time = 0
