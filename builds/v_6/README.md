- Скрипт, отсылает скрин экрана в чат телеграм или вк через бота по нажатию на колесико мыши.
- Скрипт использует конфиг в виде `config.json` файла, который обязательно должен 
лежать в одной папке со скриптом, со следующими обязательными полями 
(необязательные поля можно посмотреть [здесь](../../docs/all_settings.md)):
- Если хотите слать в телергам:
  - bot_token - (str) токен бота (в формате 0000000:aaaaaaa...)
  - chat_id - (str) id чата в телеграмме (может быть отрицательным)
  - пример:
  ```json
  {
    "bot_token": "0000000000:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "chat_id": "-1000000000000"
  }
  ```
- Если хотите слать в VK:
  - screener - (str) куда слать скрины "vk"
  - printer - (str) куда писать логи работы "vk"
  - vk
    - token - (str) токен бота (в формате vk1.a.XXXXXXXXXXXXXX...)
    - peer_id - (str) peer чата в VK (если создавали чат в сообществе, то 2000000001)
  - пример:
  ```json
  {
    "screener": "vk",
    "printer": "vk",
    "vk": {
      "token": "vk1.a.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
      "peer_id": 2000000001
    }
  }
  ```
