# Simple-moderation-telegram-bot
Russian Documentation


Требования
Python 3.6+
Установленные библиотеки: telebot, json, re, datetime, os, logging
Установка
Скачайте файл bot.py
Установите зависимости:
bash


1
pip install telebot
Настройка конфига (config.json)
json


1
2
3
4
5
6
7
8
⌄
{
  "token": "YOUR_BOT_TOKEN",
  "admins": ["admin1", "admin2"],
  "banned_words": ["слово1", "слово2"],
  "notcensure_words": ["мат1", "мат2"],
  "banned_mute_duration": 24.0,
  "mat_mute_duration": 1.0
}
Пояснения:

admins — список логинов администраторов (без @)
banned_words — список запрещённых слов (мут за обнаружение)
notcensure_words — список матов (мут за обнаружение, несмотря на название переменной)
banned_mute_duration — длительность мута за запрещённые слова (часы)
mat_mute_duration — длительность мута за маты (часы)
Использование
Автоматическая модерация:

Бот автоматически проверяет все сообщения на наличие:
Запрещённых слов (banned_words)
Матов (notcensure_words)
При обнаружении:
Накладывается мут
В чат отправляется уведомление
Действие логируется
Ручной мут (только для админов):

text


1
2
Мут 2 часа @username
Мут 30 минут @username
Доступно только администраторам
Время указывается в часах/минутах
Мут применяется с указанием администратора
Логирование
Все действия логируются в папку logs
Логи автоматически удаляются через 7 дней
Пример лога:
[14:30:22] @admin muted @user (for forbidden word: "слово1")
English Documentation

Requirements
Python 3.6+
Installed libraries: telebot, json, re, datetime, os, logging
Installation
Download bot.py file
Install dependencies:
bash


1
pip install telebot
Configuration (config.json)
json


1
2
3
4
5
6
7
8
⌄
{
  "token": "YOUR_BOT_TOKEN",
  "admins": ["admin1", "admin2"],
  "banned_words": ["word1", "word2"],
  "notcensure_words": ["curse1", "curse2"],
  "banned_mute_duration": 24.0,
  "mat_mute_duration": 1.0
}
Explanations:

admins — list of administrator usernames (without @)
banned_words — list of forbidden words (mutes on detection)
notcensure_words — list of profanity (mutes on detection, despite variable name)
banned_mute_duration — mute duration for banned words (hours)
mat_mute_duration — mute duration for profanity (hours)
Usage
Automatic Moderation:

The bot automatically checks all messages for:
Forbidden words (banned_words)
Profanity (notcensure_words)
On detection:
Mute is applied
Notification is sent to the chat
Action is logged
Manual Mute (for admins only):

text


1
2
Mute 2 hours @username
Mute 30 minutes @username
Available only to administrators
Time specified in hours/minutes
Mute includes administrator's username
Logging
All actions are logged in the logs folder
Logs are automatically deleted after 7 days
Log example:
[14:30:22] @admin muted @user (for forbidden word: "word1")
