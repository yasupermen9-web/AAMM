# AAMM

# 📊 Трекер настроения и продуктивности

Telegram-бот для ежедневного отслеживания настроения, работы и сна.
Бот собирает данные и выявляет закономерности: как сон влияет на настроение, в какие дни ты продуктивнее и многое другое.

---

## 🗂 Структура проекта

```
mood_tracker_bot/
├── bot.py           — точка входа, все хэндлеры
├── db_handler.py    — работа с базой данных
├── analyzer.py      — статистика, инсайты, графики
├── keyboards.py     — все клавиатуры (Reply + Inline)
├── messages.py      — все тексты сообщений
├── reminders.py     — ежедневные напоминания
├── schema.sql       — структура базы данных
├── test_data.sql    — тестовые данные
└── requirements.txt — зависимости
```

---

## ⚙️ Установка и запуск

**1. Клонируй репозиторий**
```bash
git clone https://github.com/your_username/mood_tracker_bot.git
cd mood_tracker_bot
```

**2. Создай виртуальное окружение**
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

**3. Установи зависимости**
```bash
pip install -r requirements.txt
```

**4. Создай файл `.env` с токеном бота**
```
BOT_TOKEN=your_telegram_bot_token_here
```
Токен получить у [@BotFather](https://t.me/BotFather) в Telegram.

**5. Запусти бота**
```bash
python bot.py
```

---

## 📋 Команды бота

| Команда         | Кнопка           | Действие                              |
|-----------------|------------------|---------------------------------------|
| `/start`        | —                | Приветствие и регистрация             |
| `/add`          | ➕ Записать день  | Ввод данных за сегодня                |
| `/stats`        | 📊 Статистика     | Статистика, инсайты, график           |
| `/history`      | 📋 История        | Последние 10 записей                  |
| `/settings`     | ⚙️ Настройки      | Изменить время напоминания            |
| `/clear`        | —                | Удалить все данные                    |
| `/help`         | —                | Справка                               |

---

## 🗄 Схема базы данных

**Таблица `users`**
| Поле         | Тип     | Описание                    |
|--------------|---------|-----------------------------|
| user_id      | INTEGER | Telegram ID пользователя    |
| username     | TEXT    | Имя пользователя            |
| created_at   | TEXT    | Дата регистрации            |
| remind_time  | TEXT    | Время напоминания (ЧЧ:ММ)  |

**Таблица `daily_records`**
| Поле         | Тип     | Описание                    |
|--------------|---------|-----------------------------|
| id           | INTEGER | Первичный ключ              |
| user_id      | INTEGER | Ссылка на пользователя      |
| record_date  | TEXT    | Дата записи (YYYY-MM-DD)    |
| mood         | INTEGER | Настроение от 1 до 5        |
| work_hours   | REAL    | Часы работы/учёбы           |
| sleep_hours  | REAL    | Часы сна                    |
| comment      | TEXT    | Заметка (опционально)       |

---

## 📦 Стек

- **Python 3.10+**
- **pyTelegramBotAPI** — Telegram Bot API
- **sqlite3** — база данных (встроен в Python)
- **matplotlib** — построение графиков
- **python-dotenv** — хранение токена в .env
