import matplotlib
matplotlib.use("Agg")  # без GUI — для серверного запуска
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

from messages import MOOD_EMOJIS


def get_week_summary(records):
    """
    Принимает список записей за неделю.
    Возвращает текст со статистикой.
    """
    if not records:
        return None

    moods       = [r["mood"]        for r in records]
    works       = [r["work_hours"]  for r in records]
    sleeps      = [r["sleep_hours"] for r in records]

    avg_mood  = sum(moods)  / len(moods)
    avg_work  = sum(works)  / len(works)
    avg_sleep = sum(sleeps) / len(sleeps)

    best_mood_record = max(records, key=lambda r: r["mood"])
    best_work_record = max(records, key=lambda r: r["work_hours"])

    best_mood_date = _format_date(best_mood_record["record_date"])
    best_work_date = _format_date(best_work_record["record_date"])

    text = (
        f"📊 <b>Статистика за неделю</b> ({len(records)} дн.)\n\n"
        f"😊 Среднее настроение:  <b>{avg_mood:.1f}/5</b>\n"
        f"📚 Средние часы работы: <b>{avg_work:.1f} ч</b>\n"
        f"😴 Средний сон:         <b>{avg_sleep:.1f} ч</b>\n\n"
        f"🏆 Лучшее настроение:   {best_mood_date} — {MOOD_EMOJIS[best_mood_record['mood']]} {best_mood_record['mood']}/5\n"
        f"⚡ Самый продуктивный:  {best_work_date} — {best_work_record['work_hours']} ч"
    )
    return text


def get_month_summary(records):
    """То же, что get_week_summary, но для месяца."""
    if not records:
        return None

    moods  = [r["mood"]        for r in records]
    works  = [r["work_hours"]  for r in records]
    sleeps = [r["sleep_hours"] for r in records]

    avg_mood  = sum(moods)  / len(moods)
    avg_work  = sum(works)  / len(works)
    avg_sleep = sum(sleeps) / len(sleeps)

    best_mood_record = max(records, key=lambda r: r["mood"])
    best_work_record = max(records, key=lambda r: r["work_hours"])

    best_mood_date = _format_date(best_mood_record["record_date"])
    best_work_date = _format_date(best_work_record["record_date"])

    text = (
        f"🗓 <b>Статистика за месяц</b> ({len(records)} дн.)\n\n"
        f"😊 Среднее настроение:  <b>{avg_mood:.1f}/5</b>\n"
        f"📚 Средние часы работы: <b>{avg_work:.1f} ч</b>\n"
        f"😴 Средний сон:         <b>{avg_sleep:.1f} ч</b>\n\n"
        f"🏆 Лучшее настроение:   {best_mood_date} — {MOOD_EMOJIS[best_mood_record['mood']]} {best_mood_record['mood']}/5\n"
        f"⚡ Самый продуктивный:  {best_work_date} — {best_work_record['work_hours']} ч"
    )
    return text


def get_insights(records):
    """
    Анализирует данные и выдаёт персональные инсайты.
    Нужно минимум 5 записей.
    """
    if len(records) < 5:
        return "📈 Нужно больше данных для инсайтов. Записывай дни хотя бы неделю подряд!"

    insights = []

    # Инсайт 1: влияние сна на настроение
    good_sleep = [r for r in records if r["sleep_hours"] >= 7.5]
    bad_sleep  = [r for r in records if r["sleep_hours"] <  7.5]

    if good_sleep and bad_sleep:
        avg_mood_good_sleep = sum(r["mood"] for r in good_sleep) / len(good_sleep)
        avg_mood_bad_sleep  = sum(r["mood"] for r in bad_sleep)  / len(bad_sleep)
        diff = avg_mood_good_sleep - avg_mood_bad_sleep

        if diff > 0.3:
            insights.append(
                f"😴 Когда ты спишь 7.5+ часов, настроение выше на <b>{diff:.1f} балла</b>"
            )
        elif diff < -0.3:
            insights.append(
                "😴 Интересно: больше сна не всегда улучшает твоё настроение"
            )

    # Инсайт 2: связь работы и настроения
    productive_days = [r for r in records if r["work_hours"] >= 4]
    lazy_days       = [r for r in records if r["work_hours"] <  4]

    if productive_days and lazy_days:
        avg_mood_productive = sum(r["mood"] for r in productive_days) / len(productive_days)
        avg_mood_lazy       = sum(r["mood"] for r in lazy_days)       / len(lazy_days)
        diff = avg_mood_productive - avg_mood_lazy

        if diff > 0.3:
            insights.append(
                f"📚 В продуктивные дни (4+ часов работы) настроение выше на <b>{diff:.1f} балла</b>"
            )
        elif diff < -0.3:
            insights.append(
                f"📚 В дни с меньшей нагрузкой твоё настроение лучше на <b>{abs(diff):.1f} балла</b>"
            )

    # Инсайт 3: лучший день недели
    days_ru = {0: "Пн", 1: "Вт", 2: "Ср", 3: "Чт", 4: "Пт", 5: "Сб", 6: "Вс"}
    mood_by_weekday = {}

    for r in records:
        weekday = datetime.strptime(r["record_date"], "%Y-%m-%d").weekday()
        if weekday not in mood_by_weekday:
            mood_by_weekday[weekday] = []
        mood_by_weekday[weekday].append(r["mood"])

    if len(mood_by_weekday) >= 3:
        avg_by_day = {
            day: sum(moods) / len(moods)
            for day, moods in mood_by_weekday.items()
        }
        best_day  = max(avg_by_day, key=avg_by_day.get)
        worst_day = min(avg_by_day, key=avg_by_day.get)

        insights.append(
            f"📅 Твой лучший день недели: <b>{days_ru[best_day]}</b>, "
            f"сложнее всего: <b>{days_ru[worst_day]}</b>"
        )

    if not insights:
        return "📈 Данных пока маловато для выводов. Продолжай вести записи!"

    result = "🔍 <b>Твои инсайты:</b>\n\n" + "\n\n".join(f"• {i}" for i in insights)
    return result


def generate_chart(records, user_id):
    """
    Строит график по трём показателям.
    Сохраняет PNG и возвращает путь к файлу.
    """
    dates  = [datetime.strptime(r["record_date"], "%Y-%m-%d") for r in records]
    moods  = [r["mood"]        for r in records]
    works  = [r["work_hours"]  for r in records]
    sleeps = [r["sleep_hours"] for r in records]

    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Левая ось — настроение
    ax1.set_ylabel("Настроение (1–5)", color="#E07B39")
    ax1.plot(dates, moods, color="#E07B39", marker="o", linewidth=2, label="Настроение")
    ax1.set_ylim(0, 6)
    ax1.tick_params(axis="y", labelcolor="#E07B39")

    # Правая ось — часы
    ax2 = ax1.twinx()
    ax2.set_ylabel("Часы", color="#5B9BD5")
    ax2.plot(dates, works,  color="#5B9BD5", marker="s", linewidth=2, linestyle="--", label="Работа")
    ax2.plot(dates, sleeps, color="#70AD47", marker="^", linewidth=2, linestyle=":",  label="Сон")
    ax2.set_ylim(0, 14)
    ax2.tick_params(axis="y", labelcolor="#5B9BD5")

    # Форматирование дат по оси X
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
    fig.autofmt_xdate()

    # Заголовок и легенда
    ax1.set_title("Динамика настроения, работы и сна", fontsize=13, pad=12)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    ax1.grid(True, alpha=0.3)
    fig.tight_layout()

    # Сохраняем во временный файл
    chart_path = f"chart_{user_id}.png"
    plt.savefig(chart_path, dpi=120)
    plt.close()

    return chart_path


# ─── Вспомогательная функция ───

def _format_date(date_str):
    """Превращает '2025-06-01' в '01.06'."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%d.%m")
