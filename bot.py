import telebot
import json
import re
import datetime
import os
import logging
from telebot.types import Chat, ChatMember

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загрузка конфига
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# Инициализация бота
bot = telebot.TeleBot(config["token"])

# Поля из конфига
ADMINS = set(config["admins"])
NOT_CENSOR_WORDS = set(config["notcensure_words"])
BANNED_WORDS = set(config["banned_words"])
BANNED_MUTE_DURATION = float(config["banned_mute_duration"])
MAT_MUTE_DURATION = float(config["mat_mute_duration"])

# Создание папки для логов
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Генерация уникального имени лог-файла
def get_log_filename():
    return os.path.join(LOG_DIR, f"bot_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Логирование действий
def log_action(action_type, admin_username, user_username, details=None):
    log_entry = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] @{admin_username} {action_type} @{user_username}"
    if details:
        log_entry += f" ({details})"
    logger.info(log_entry)

# Проверка прав администратора в чате
def is_admin(chat_id, user_id):
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['administrator', 'creator']
    except Exception as e:
        logger.error(f"Ошибка проверки прав администратора: {e}")
        return False

# Применение мута
def apply_mute(chat_id, user_id, duration_hours, admin_username):
    try:
        # Проверка прав бота
        if not is_admin(chat_id, bot.get_me().id):
            logger.warning("Бот не является администратором в этом чате.")
            return

        until_date = (datetime.datetime.now() + datetime.timedelta(hours=duration_hours)).timestamp()
        bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
            until_date=until_date
        )
        log_action("muted", admin_username, user_username, f"mute time {duration_hours} hours")
        bot.send_message(
            chat_id,
            f"Пользователь @{user_username} замучен до {datetime.datetime.fromtimestamp(until_date).strftime('%Y-%m-%d %H:%M')} "
            f"Администратор: {admin_username}"
        )
    except Exception as e:
        logger.error(f"Ошибка при муте: {e}")

# Нормализация и проверка текста
def normalize_and_check(text, chat_id, user_id, user_username):
    # Словарь замен символов
    char_replacements = {
        '@': 'a', '3': 'з', '1': 'и', '0': 'о', '5': 'с', '7': 'т', '9': 'р',
        'x': 'х', 'X': 'х', 's': 'с', 'S': 'с', 'z': 'з', 'Z': 'з', 'a': 'а', 'A': 'а',
        'e': 'е', 'E': 'е', 'o': 'о', 'O': 'о', 'i': 'и', 'I': 'и', 't': 'т', 'T': 'т',
        'b': 'б', 'B': 'б', 'p': 'р', 'P': 'р', 'k': 'к', 'K': 'к', 'm': 'м', 'M': 'м',
        'y': 'у', 'Y': 'у', 'n': 'н', 'N': 'н', 'l': 'л', 'L': 'л', 'c': 'с', 'C': 'с',
        'd': 'д', 'D': 'д', 'f': 'ф', 'F': 'ф', 'g': 'г', 'G': 'г', 'h': 'х', 'H': 'х',
        'j': 'ж', 'J': 'ж', 'q': 'к', 'Q': 'к', 'w': 'в', 'W': 'в', 'v': 'в', 'V': 'в',
        'u': 'у', 'U': 'у', 'r': 'р', 'R': 'р', 'k': 'к', 'K': 'к', 'b': 'б', 'B': 'б'
    }

    # Замена чисел
    text = re.sub(r'\b3\.14\b', 'пи', text, flags=re.IGNORECASE)
    text = re.sub(r'\b1\.618\b', 'фи', text, flags=re.IGNORECASE)

    # Нормализация
    normalized = ''.join([char_replacements.get(c, c) for c in text]).lower()
    normalized = re.sub(r'[^a-zа-я\s.]', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()

    # Проверка на запрещённые слова
    for word in BANNED_WORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', normalized):
            apply_mute(chat_id, user_id, BANNED_MUTE_DURATION, "system")
            log_action("muted", "system", user_username, f"for forbidden word: {word}")
            return

    # Проверка на маты
    for word in MAT_WORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', normalized):
            apply_mute(chat_id, user_id, MAT_MUTE_DURATION, "system")
            log_action("muted", "system", user_username, f"for mat: {word}")
            return

    return normalized

# Удаление старых логов
def cleanup_old_logs():
    now = datetime.datetime.now()
    retention_period = datetime.timedelta(days=7)

    for filename in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, filename)
        if os.path.isfile(file_path):
            try:
                file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                if now - file_mtime > retention_period:
                    os.remove(file_path)
                    logger.info(f"Удалён старый лог: {filename}")
            except Exception as e:
                logger.error(f"Ошибка удаления лога {filename}: {e}")

# Обработчик сообщений
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    # Проверка на администратора
    if not is_admin(message.chat.id, message.from_user.id):
        user_username = message.from_user.username or "unknown"
        normalized_text = normalize_and_check(message.text, message.chat.id, message.from_user.id, user_username)
        logger.info(f"Нормализованная строка: {normalized_text}")
        return

    # Обработка команды мута
    text = message.text
    if text.startswith(("Мут", "мут")):
        parts = text.split()
        if len(parts) < 4 or parts[0].lower() != "мут":
            logger.warning("Некорректный формат команды мута.")
            return

        try:
            duration_str = parts[1]
            unit = parts[2].lower()
            username = parts[3][1:]

            # Конвертация времени
            if unit == "часов":
                duration_hours = int(duration_str)
            elif unit == "минут":
                duration_hours = int(duration_str) / 60
            else:
                logger.warning(f"Некорректная единица измерения: {unit}")
                return

            # Получение ID пользователя
            try:
                user = bot.get_chat(username)
                apply_mute(message.chat.id, user.id, duration_hours, message.from_user.username)
            except Exception as e:
                logger.error(f"Ошибка при муте: {e}")
        except Exception as e:
            logger.error(f"Ошибка обработки команды мута: {e}")

# Запуск бота
if __name__ == "__main__":
    cleanup_old_logs()
    bot.polling(none_stop=True)
