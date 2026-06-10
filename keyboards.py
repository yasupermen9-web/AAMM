import telebot.types as types


def main_menu():
    """Главное меню — постоянная клавиатура внизу экрана."""
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("➕ Записать день", "📊 Статистика")
    kb.row("📋 История",       "⚙️ Настройки")
    return kb


def mood_keyboard():
    """Инлайн-кнопки для выбора настроения (1–5)."""
    kb = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton("1 😞", callback_data="mood_1"),
        types.InlineKeyboardButton("2 😐", callback_data="mood_2"),
        types.InlineKeyboardButton("3 🙂", callback_data="mood_3"),
        types.InlineKeyboardButton("4 😊", callback_data="mood_4"),
        types.InlineKeyboardButton("5 🤩", callback_data="mood_5"),
    ]
    kb.row(*buttons)
    return kb


def hours_keyboard(prefix):
    """
    Инлайн-кнопки для быстрого выбора часов.
    prefix — 'work' или 'sleep', чтобы различать callback.
    """
    kb = types.InlineKeyboardMarkup()

    if prefix == "work":
        values = ["0.5", "1", "2", "4"]
    else:
        values = ["6", "7", "8", "9"]

    buttons = [
        types.InlineKeyboardButton(f"{v} ч", callback_data=f"{prefix}_{v}")
        for v in values
    ]
    buttons.append(types.InlineKeyboardButton("Другое...", callback_data=f"{prefix}_custom"))

    kb.row(*buttons)
    return kb


def skip_keyboard():
    """Инлайн-кнопка «Пропустить» для комментария."""
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Пропустить", callback_data="comment_skip"))
    return kb


def stats_menu_keyboard():
    """Инлайн-меню выбора периода статистики."""
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("📅 За неделю",  callback_data="stats_week"),
        types.InlineKeyboardButton("🗓 За месяц",   callback_data="stats_month"),
    )
    kb.row(
        types.InlineKeyboardButton("🔍 Инсайты",    callback_data="stats_insights"),
        types.InlineKeyboardButton("📉 График",      callback_data="stats_chart"),
    )
    return kb


def confirm_clear_keyboard():
    """Инлайн-кнопки подтверждения удаления данных."""
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("✅ Да, удалить всё", callback_data="clear_yes"),
        types.InlineKeyboardButton("❌ Отмена",           callback_data="clear_no"),
    )
    return kb
