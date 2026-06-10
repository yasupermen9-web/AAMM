import telebot
from dotenv import dotenv_values
from pathlib import Path
from datetime import date

import db_handler
import analyzer
import keyboards
import reminders
from messages import (
    WELCOME, HELP, ASK_MOOD, ASK_WORK, ASK_SLEEP, ASK_COMMENT,
    ASK_REMIND_TIME, WRONG_TIME_FORMAT, WRONG_NUMBER, ENTER_CUSTOM_HOURS,
    RECORD_SAVED, NO_DATA, STATS_MENU, CLEAR_CONFIRM, CLEAR_DONE,
    CLEAR_CANCEL, REMIND_UPDATED, SETTINGS_INFO, MOOD_EMOJIS
)

config = dotenv_values(".env")
bot = telebot.TeleBot(config["BOT_TOKEN"], parse_mode="HTML")

# Хранилище текущих состояний пользователей
# Ключ — user_id, значение — словарь с шагом и данными
user_states = {}

# Возможные шаги при вводе данных
STEP_MOOD       = "mood"
STEP_WORK       = "work"
STEP_SLEEP      = "sleep"
STEP_COMMENT    = "comment"
STEP_REMIND     = "remind"

# Шаги, где ждём текстовый ввод числа
STEP_WORK_CUSTOM  = "work_custom"
STEP_SLEEP_CUSTOM = "sleep_custom"


# ─── Команды ───────────────────────────────────────────────────────────────────

@bot.message_handler(commands=["start"])
def cmd_start(message):
    user_id  = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    db_handler.add_user(user_id, username)

    bot.send_message(
        user_id,
        WELCOME.format(name=message.from_user.first_name),
        reply_markup=keyboards.main_menu()
    )


@bot.message_handler(commands=["help"])
def cmd_help(message):
    bot.send_message(message.from_user.id, HELP)


@bot.message_handler(commands=["add"])
def cmd_add(message):
    start_adding(message.from_user.id)


@bot.message_handler(commands=["stats"])
def cmd_stats(message):
    bot.send_message(
        message.from_user.id,
        STATS_MENU,
        reply_markup=keyboards.stats_menu_keyboard()
    )


@bot.message_handler(commands=["history"])
def cmd_history(message):
    show_history(message.from_user.id)


@bot.message_handler(commands=["settings"])
def cmd_settings(message):
    user_id     = message.from_user.id
    remind_time = db_handler.get_remind_time(user_id)

    user_states[user_id] = {"step": STEP_REMIND}
    bot.send_message(user_id, SETTINGS_INFO.format(time=remind_time))


@bot.message_handler(commands=["clear"])
def cmd_clear(message):
    bot.send_message(
        message.from_user.id,
        CLEAR_CONFIRM,
        reply_markup=keyboards.confirm_clear_keyboard()
    )


# ─── Кнопки главного меню ──────────────────────────────────────────────────────

@bot.message_handler(func=lambda m: m.text == "➕ Записать день")
def menu_add(message):
    start_adding(message.from_user.id)


@bot.message_handler(func=lambda m: m.text == "📊 Статистика")
def menu_stats(message):
    bot.send_message(
        message.from_user.id,
        STATS_MENU,
        reply_markup=keyboards.stats_menu_keyboard()
    )


@bot.message_handler(func=lambda m: m.text == "📋 История")
def menu_history(message):
    show_history(message.from_user.id)


@bot.message_handler(func=lambda m: m.text == "⚙️ Настройки")
def menu_settings(message):
    user_id     = message.from_user.id
    remind_time = db_handler.get_remind_time(user_id)

    user_states[user_id] = {"step": STEP_REMIND}
    bot.send_message(user_id, SETTINGS_INFO.format(time=remind_time))


# ─── Текстовый ввод ────────────────────────────────────────────────────────────

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = message.from_user.id
    state   = user_states.get(user_id)

    if not state:
        return

    step = state.get("step")

    # Ввод своего числа часов работы
    if step == STEP_WORK_CUSTOM:
        hours = parse_float(message.text)
        if hours is None:
            bot.send_message(user_id, WRONG_NUMBER)
            return
        state["work_hours"] = hours
        state["step"] = STEP_SLEEP
        bot.send_message(user_id, ASK_SLEEP, reply_markup=keyboards.hours_keyboard("sleep"))

    # Ввод своего числа часов сна
    elif step == STEP_SLEEP_CUSTOM:
        hours = parse_float(message.text)
        if hours is None:
            bot.send_message(user_id, WRONG_NUMBER)
            return
        state["sleep_hours"] = hours
        state["step"] = STEP_COMMENT
        bot.send_message(user_id, ASK_COMMENT, reply_markup=keyboards.skip_keyboard())

    # Ввод комментария текстом
    elif step == STEP_COMMENT:
        state["comment"] = message.text
        finish_adding(user_id)

    # Ввод нового времени напоминания
    elif step == STEP_REMIND:
        time_str = message.text.strip()
        if not is_valid_time(time_str):
            bot.send_message(user_id, WRONG_TIME_FORMAT)
            return
        db_handler.update_remind_time(user_id, time_str)
        user_states.pop(user_id, None)
        bot.send_message(user_id, REMIND_UPDATED.format(time=time_str))


# ─── Инлайн-кнопки ─────────────────────────────────────────────────────────────

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    data    = call.data
    state   = user_states.get(user_id, {})

    bot.answer_callback_query(call.id)  # убирает «часики» на кнопке

    # ── Выбор настроения ──
    if data.startswith("mood_"):
        mood = int(data.split("_")[1])
        state["mood"] = mood
        state["step"] = STEP_WORK
        user_states[user_id] = state

        bot.edit_message_text(
            f"Настроение: {MOOD_EMOJIS[mood]} {mood}/5 — принято!",
            call.message.chat.id, call.message.message_id
        )
        bot.send_message(user_id, ASK_WORK, reply_markup=keyboards.hours_keyboard("work"))

    # ── Выбор часов работы ──
    elif data.startswith("work_"):
        value = data.split("_")[1]

        if value == "custom":
            state["step"] = STEP_WORK_CUSTOM
            user_states[user_id] = state
            bot.send_message(user_id, ENTER_CUSTOM_HOURS)
        else:
            state["work_hours"] = float(value)
            state["step"] = STEP_SLEEP
            user_states[user_id] = state

            bot.edit_message_text(
                f"Работа/учёба: {value} ч — принято!",
                call.message.chat.id, call.message.message_id
            )
            bot.send_message(user_id, ASK_SLEEP, reply_markup=keyboards.hours_keyboard("sleep"))

    # ── Выбор часов сна ──
    elif data.startswith("sleep_"):
        value = data.split("_")[1]

        if value == "custom":
            state["step"] = STEP_SLEEP_CUSTOM
            user_states[user_id] = state
            bot.send_message(user_id, ENTER_CUSTOM_HOURS)
        else:
            state["sleep_hours"] = float(value)
            state["step"] = STEP_COMMENT
            user_states[user_id] = state

            bot.edit_message_text(
                f"Сон: {value} ч — принято!",
                call.message.chat.id, call.message.message_id
            )
            bot.send_message(user_id, ASK_COMMENT, reply_markup=keyboards.skip_keyboard())

    # ── Пропуск комментария ──
    elif data == "comment_skip":
        state["comment"] = None
        user_states[user_id] = state

        bot.edit_message_text(
            "Комментарий пропущен.",
            call.message.chat.id, call.message.message_id
        )
        finish_adding(user_id)

    # ── Меню статистики ──
    elif data == "stats_week":
        records = db_handler.get_week_stats(user_id)
        text    = analyzer.get_week_summary(records) or NO_DATA
        bot.send_message(user_id, text)

    elif data == "stats_month":
        records = db_handler.get_month_stats(user_id)
        text    = analyzer.get_month_summary(records) or NO_DATA
        bot.send_message(user_id, text)

    elif data == "stats_insights":
        records = db_handler.get_month_stats(user_id)
        text    = analyzer.get_insights(records)
        bot.send_message(user_id, text)

    elif data == "stats_chart":
        records = db_handler.get_month_stats(user_id)

        if not records:
            bot.send_message(user_id, NO_DATA)
            return

        bot.send_message(user_id, "Строю график... 📉")
        chart_path = analyzer.generate_chart(records, user_id)

        with open(chart_path, "rb") as photo:
            bot.send_photo(user_id, photo)

        Path(chart_path).unlink()  # удаляем временный файл

    # ── Очистка данных ──
    elif data == "clear_yes":
        db_handler.delete_all_records(user_id)
        bot.edit_message_text(CLEAR_DONE, call.message.chat.id, call.message.message_id)

    elif data == "clear_no":
        bot.edit_message_text(CLEAR_CANCEL, call.message.chat.id, call.message.message_id)


# ─── Вспомогательные функции ───────────────────────────────────────────────────

def start_adding(user_id):
    """Начинает процесс ввода данных за сегодня."""
    user_states[user_id] = {"step": STEP_MOOD}
    bot.send_message(user_id, ASK_MOOD, reply_markup=keyboards.mood_keyboard())


def finish_adding(user_id):
    """Сохраняет запись и отправляет подтверждение."""
    state = user_states.pop(user_id, {})

    mood        = state.get("mood")
    work_hours  = state.get("work_hours")
    sleep_hours = state.get("sleep_hours")
    comment     = state.get("comment")

    db_handler.save_record(user_id, mood, work_hours, sleep_hours, comment)

    comment_line = f"💬 {comment}" if comment else ""
    today_str    = date.today().strftime("%d.%m.%Y")

    text = RECORD_SAVED.format(
        date        = today_str,
        mood_emoji  = MOOD_EMOJIS[mood],
        mood        = mood,
        work        = work_hours,
        sleep       = sleep_hours,
        comment_line= comment_line
    )
    bot.send_message(user_id, text)


def show_history(user_id):
    """Отправляет последние 10 записей."""
    records = db_handler.get_all_records(user_id)[:10]

    if not records:
        bot.send_message(user_id, NO_DATA)
        return

    lines = ["📋 <b>Последние записи:</b>\n"]
    for r in records:
        date_str = r["record_date"][5:]  # берём MM-DD
        date_str = date_str.replace("-", ".")
        emoji    = MOOD_EMOJIS[r["mood"]]
        lines.append(
            f"📅 {date_str}  {emoji} {r['mood']}  |  📚 {r['work_hours']}ч  |  😴 {r['sleep_hours']}ч"
        )

    bot.send_message(user_id, "\n".join(lines))


def parse_float(text):
    """Пробует превратить строку в число. Возвращает None при ошибке."""
    try:
        value = float(text.replace(",", "."))
        if value < 0 or value > 24:
            return None
        return value
    except ValueError:
        return None


def is_valid_time(time_str):
    """Проверяет, что строка вида ЧЧ:ММ корректна."""
    try:
        parts = time_str.split(":")
        if len(parts) != 2:
            return False
        hour, minute = int(parts[0]), int(parts[1])
        return 0 <= hour <= 23 and 0 <= minute <= 59
    except ValueError:
        return False


# ─── Запуск ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    db_handler.init_db()
    reminders.start_reminder_thread(bot)

    print("Бот запущен ✅")
    bot.infinity_polling()
