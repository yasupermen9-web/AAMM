import threading
import time
from datetime import datetime

import db_handler
from messages import REMINDER_TEXT


def send_reminders(bot):
    """
    Каждую минуту проверяет всех пользователей.
    Если текущее время совпадает с remind_time — отправляет напоминание.
    """
    sent_today = set()  # чтобы не слать одному человеку дважды за минуту

    while True:
        now = datetime.now().strftime("%H:%M")

        # Сбрасываем список в полночь
        if now == "00:00":
            sent_today.clear()

        users = db_handler.get_all_users()

        for user in users:
            user_id     = user["user_id"]
            remind_time = user["remind_time"]

            if now == remind_time and user_id not in sent_today:
                try:
                    bot.send_message(user_id, REMINDER_TEXT)
                    sent_today.add(user_id)
                except Exception:
                    # Пользователь мог заблокировать бота — просто пропускаем
                    pass

        time.sleep(60)  # ждём минуту


def start_reminder_thread(bot):
    """Запускает поток напоминаний в фоне."""
    thread = threading.Thread(target=send_reminders, args=(bot,), daemon=True)
    thread.start()
