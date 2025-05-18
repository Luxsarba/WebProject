import matplotlib.pyplot as plt
import io
import sqlalchemy as sa
from datetime import datetime, timedelta
from data.expenses import Expense
from data.categories import Category


def _get_start_date(period):
    now = datetime.now()
    if period == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "month":
        return now - timedelta(days=30)
    else:
        return now - timedelta(days=7)


def _get_period_name(period):
    period_names = {
        "today": "сегодня",
        "week": "неделя",
        "month": "месяц"
    }
    return period_names.get(period, "неделя")


def build_pie_chart(session, user_id, period="week"):
    start_date = _get_start_date(period)
    results = (
        session.query(Category.name, sa.func.sum(Expense.amount))
        .join(Expense, Category.id == Expense.category_id)
        .filter(Expense.user_id == user_id, Expense.date >= start_date)
        .group_by(Category.name)
        .all()
    )
    if not results:
        return None

    labels, values = zip(*results)
    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=140)
    ax.axis("equal")
    plt.title(f"Расходы по категориям ({_get_period_name(period)})")
    return _fig_to_buf(fig)


def build_bar_chart(session, user_id, period="week"):
    start_date = _get_start_date(period)
    expenses = (
        session.query(Expense.date, sa.func.sum(Expense.amount))
        .filter(Expense.user_id == user_id, Expense.date >= start_date)
        .group_by(sa.func.date(Expense.date))
        .order_by(Expense.date)
        .all()
    )
    if not expenses:
        return None

    dates = [d.strftime("%d.%m") for d, _ in expenses]
    values = [v for _, v in expenses]

    fig, ax = plt.subplots()
    ax.bar(dates, values, color="skyblue")
    plt.xticks(rotation=45)
    plt.title(f"Ежедневные расходы ({_get_period_name(period)})")
    plt.ylabel("Сумма, ₽")
    return _fig_to_buf(fig)


def build_line_chart(session, user_id, period="week"):
    start_date = _get_start_date(period)
    expenses = (
        session.query(Expense.date, Expense.amount)
        .filter(Expense.user_id == user_id, Expense.date >= start_date)
        .order_by(Expense.date)
        .all()
    )
    if not expenses:
        return None

    daily_sums = {}
    for date, amount in expenses:
        key = date.date()
        daily_sums[key] = daily_sums.get(key, 0) + amount

    dates = sorted(daily_sums)
    cumulative = []
    total = 0
    for d in dates:
        total += daily_sums[d]
        cumulative.append(total)

    fig, ax = plt.subplots()
    ax.plot([d.strftime("%d.%m") for d in dates], cumulative, marker='o', linestyle='-')
    plt.xticks(rotation=45)
    plt.title(f"Накопленные расходы ({_get_period_name(period)})")
    plt.ylabel("Сумма, ₽")
    return _fig_to_buf(fig)


def _fig_to_buf(fig):
    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)
    return buf
