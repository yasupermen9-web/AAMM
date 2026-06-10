import sqlite3
from datetime import date, datetime, timedelta

DB_FILE = "mood_tracker.db"


def get_connection():
    """Открывает соединение с базой данных."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # чтобы обращаться к полям по имени
    return conn


def init_db():
    """Создаёт таблицы при первом запуске."""
    with open("schema.sql", "r", encoding="utf-8") as f:
        sql = f.read()

    with get_connection() as conn:
        conn.executescript(sql)


def add_user(user_id, username):
    """Добавляет пользователя, если его ещё нет."""
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )


def save_record(user_id, mood, work_hours, sleep_hours, comment=None):
    """
    Сохраняет запись за сегодня.
    Если запись уже есть — обновляет её.
    """
    today = date.today().isoformat()

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO daily_records (user_id, record_date, mood, work_hours, sleep_hours, comment)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, record_date) DO UPDATE SET
                mood        = excluded.mood,
                work_hours  = excluded.work_hours,
                sleep_hours = excluded.sleep_hours,
                comment     = excluded.comment
        """, (user_id, today, mood, work_hours, sleep_hours, comment))


def get_week_stats(user_id):
    """Возвращает записи за последние 7 дней."""
    week_ago = (date.today() - timedelta(days=7)).isoformat()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM daily_records
            WHERE user_id = ? AND record_date >= ?
            ORDER BY record_date
        """, (user_id, week_ago)).fetchall()

    return [dict(row) for row in rows]


def get_month_stats(user_id):
    """Возвращает записи за последние 30 дней."""
    month_ago = (date.today() - timedelta(days=30)).isoformat()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM daily_records
            WHERE user_id = ? AND record_date >= ?
            ORDER BY record_date
        """, (user_id, month_ago)).fetchall()

    return [dict(row) for row in rows]


def get_all_records(user_id):
    """Возвращает все записи пользователя."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM daily_records
            WHERE user_id = ?
            ORDER BY record_date DESC
        """, (user_id,)).fetchall()

    return [dict(row) for row in rows]


def update_remind_time(user_id, time_str):
    """Обновляет время ежедневного напоминания."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET remind_time = ? WHERE user_id = ?",
            (time_str, user_id)
        )


def get_remind_time(user_id):
    """Возвращает время напоминания пользователя."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT remind_time FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()

    return row["remind_time"] if row else "20:00"


def get_all_users():
    """Возвращает всех пользователей (нужно для напоминаний)."""
    with get_connection() as conn:
        rows = conn.execute("SELECT user_id, remind_time FROM users").fetchall()

    return [dict(row) for row in rows]


def delete_all_records(user_id):
    """Удаляет все записи пользователя."""
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM daily_records WHERE user_id = ?",
            (user_id,)
        )
