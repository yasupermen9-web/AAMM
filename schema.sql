-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    user_id     INTEGER PRIMARY KEY,
    username    TEXT,
    created_at  TEXT DEFAULT (datetime('now')),
    remind_time TEXT DEFAULT '20:00'
);

-- Таблица ежедневных записей
CREATE TABLE IF NOT EXISTS daily_records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER REFERENCES users(user_id),
    record_date TEXT NOT NULL,
    mood        INTEGER,
    work_hours  REAL,
    sleep_hours REAL,
    comment     TEXT,
    created_at  TEXT DEFAULT (datetime('now')),
    UNIQUE(user_id, record_date)
);

CREATE INDEX IF NOT EXISTS idx_records_user_date
    ON daily_records(user_id, record_date);
