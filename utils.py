from models import Income, Expense
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime, timedelta,date
from collections import defaultdict
import calendar

def get_total_income(db: SQLAlchemy, user_id: int) -> float:
    return db.session.query(func.sum(Income.income)).filter_by(user_id=user_id).scalar() or 0.0

def get_total_expense(db: SQLAlchemy, user_id: int) -> float:
    return db.session.query(func.sum(Expense.expense)).filter_by(user_id=user_id).scalar() or 0.0

def get_balance(db: SQLAlchemy, user_id: int) -> float:
    income = get_total_income(db, user_id)
    expense = get_total_expense(db, user_id)
    return income - expense

def get_monthly_expense(db: SQLAlchemy, user_id: int) -> float:
    first_day = date.today().replace(day=1)
    return db.session.query(func.sum(Expense.expense)).filter(
        Expense.user_id == user_id,
        Expense.date >= str(first_day)
    ).scalar() or 0.0

def get_weekly_expense(db: SQLAlchemy, user_id: int) -> float:
    last_7_days = date.today() - timedelta(days=7)
    return db.session.query(func.sum(Expense.expense)).filter(
        Expense.user_id == user_id,
        Expense.date >= str(last_7_days)
    ).scalar() or 0.0

def get_chart_data_for_period(db, user_id, chart_type, offset):
    from models import Income, Expense

    today = datetime.today()
    labels = []
    income_data = []
    expense_data = []

    if chart_type == "month":
        current_month = today.month - offset
        current_year = today.year
        while current_month <= 0:
            current_month += 12
            current_year -= 1
        
        months = []
        for i in range(2, -1, -1):
            month = current_month - i
            year = current_year
            while month <= 0:
                month += 12
                year -= 1
            months.append((year, month))

        for year, month in months:
            label = calendar.month_abbr[month] + f" {year}"
            start = datetime(year, month, 1)
            _, last_day = calendar.monthrange(year, month)
            end = datetime(year, month, last_day, 23, 59, 59)

            income = db.session.query(Income).filter(Income.user_id == user_id, Income.date >= start.strftime("%Y-%m-%d"), Income.date <= end.strftime("%Y-%m-%d")).all()
            expense = db.session.query(Expense).filter(Expense.user_id == user_id, Expense.date >= start.strftime("%Y-%m-%d"), Expense.date <= end.strftime("%Y-%m-%d")).all()

            labels.append(label)
            income_data.append(sum([inc.income for inc in income]))
            expense_data.append(sum([exp.expense for exp in expense]))

        range_label = f"{labels[0]} – {labels[-1]}"

    else:  # week
        start_of_week = today - timedelta(days=today.weekday()) - timedelta(weeks=offset)
        labels = []
        income_by_day = defaultdict(float)
        expense_by_day = defaultdict(float)

        for i in range(7):
            day = start_of_week + timedelta(days=i)
            labels.append(day.strftime("%a"))
            day_str = day.strftime("%Y-%m-%d")

            income = db.session.query(Income).filter_by(user_id=user_id, date=day_str).all()
            expense = db.session.query(Expense).filter_by(user_id=user_id, date=day_str).all()

            income_by_day[day_str] += sum([inc.income for inc in income])
            expense_by_day[day_str] += sum([exp.expense for exp in expense])

        income_data = [income_by_day[(start_of_week + timedelta(days=i)).strftime("%Y-%m-%d")] for i in range(7)]
        expense_data = [expense_by_day[(start_of_week + timedelta(days=i)).strftime("%Y-%m-%d")] for i in range(7)]

        range_label = f"{start_of_week.strftime('%b %d')} – {(start_of_week + timedelta(days=6)).strftime('%b %d')}"

    return {
        "labels": labels,
        "income": income_data,
        "expense": expense_data,
        "range_label": range_label
    }
# This code is a utility module for a Flask application that handles financial data.
# It provides functions to calculate total income, total expenses, balance, monthly and weekly expenses,