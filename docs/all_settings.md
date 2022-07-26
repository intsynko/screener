# sdds
Настройки:
- bot_token - (str) токен бота (в формате 0000000:aaaaaaa...)
- max_time - (int) максимальное время работы скрипта в минутах
- chat_id - (str) id чата в телеграмме (может быть отрицательным)
- push_message_btn - (int) код клавишы отправки скрина, изначально КОЛСИКО МЫШИ (4)
- exit_btn_code - (int) - код клавишы выхода, изначально TAB (9) [примеры клавиш](https://stackoverflow.com/questions/31363860/how-do-i-get-the-name-of-a-key-in-pywin32-giving-its-keycode)
- printer - (str) вариант уведомлений (console, telegram, window)
- commands_settings
    - pull_delay - (int) время в секндах между запросами за новыми командами
    - enabled - (bool) включены ли команды 
    - shutdown_enabled - (bool) можно ли выключать через команды 
