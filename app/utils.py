from app.models import Income, Expense
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from typing import List, Tuple

def get_total_income(db: SQLAlchemy, user_id: int) -> float:
    return db.session.query(func.sum(Income.income)).filter_by(user_id=user_id).scalar() or 0.0

def get_total_expense(db: SQLAlchemy, user_id: int) -> float:
    return db.session.query(func.sum(Expense.expense)).filter_by(user_id=user_id).scalar() or 0.0

def get_balance(db: SQLAlchemy, user_id: int) -> float:
    return get_total_income(db, user_id) - get_total_expense(db, user_id)

def get_monthly_expense(db: SQLAlchemy, user_id: int) -> float:
    first_day = date.today().replace(day=1)
    return db.session.query(func.sum(Expense.expense)).filter(
        Expense.user_id == user_id,
        Expense.date >= first_day
    ).scalar() or 0.0

def get_weekly_expense(db: SQLAlchemy, user_id: int) -> float:
    last_7_days = date.today() - timedelta(days=7)
    return db.session.query(func.sum(Expense.expense)).filter(
        Expense.user_id == user_id,
        Expense.date >= last_7_days
    ).scalar() or 0.0

def get_chart_data_for_period(
    db: SQLAlchemy,
    user_id: int,
    chart_type: str,
    offset: int = 0
) -> Tuple[List[str], List[float], List[float], str]:

    if chart_type == "week":
        today = datetime.today().date()
        start_of_week = today - timedelta(days=today.weekday()) - timedelta(weeks=offset)
        end_of_week = start_of_week + timedelta(days=6)

        labels = [(start_of_week + timedelta(days=i)).strftime("%a") for i in range(7)]
        income_totals = [0.0] * 7
        expense_totals = [0.0] * 7

        incomes = db.session.query(Income).filter(
            Income.user_id == user_id,
            Income.date.between(start_of_week, end_of_week)
        ).all()

        expenses = db.session.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.date.between(start_of_week, end_of_week)
        ).all()

        for i in incomes:
            delta = (i.date - start_of_week).days
            if 0 <= delta < 7:
                income_totals[delta] += i.income

        for e in expenses:
            delta = (e.date - start_of_week).days
            if 0 <= delta < 7:
                expense_totals[delta] += e.expense

        range_label = f"{start_of_week.strftime('%d %b')} - {end_of_week.strftime('%d %b')}"
        return labels, income_totals, expense_totals, range_label

    elif chart_type == "month":
        target_month = datetime.today().replace(day=1) - relativedelta(months=offset)
        labels = []
        income_totals = []
        expense_totals = []

        # Loop through 3 months: target and 2 before
        for i in reversed(range(3)):
            month = target_month - relativedelta(months=i)
            start_date = month.replace(day=1)
            end_date = (start_date + relativedelta(months=1)) - timedelta(days=1)
            label = month.strftime("%b")

            income_sum = db.session.query(func.sum(Income.income)).filter(
                Income.user_id == user_id,
                Income.date.between(start_date, end_date)
            ).scalar() or 0.0

            expense_sum = db.session.query(func.sum(Expense.expense)).filter(
                Expense.user_id == user_id,
                Expense.date.between(start_date, end_date)
            ).scalar() or 0.0

            labels.append(label)
            income_totals.append(income_sum)
            expense_totals.append(expense_sum)

        range_label = f"{labels[0]} - {labels[-1]}"
        return labels, income_totals, expense_totals, range_label

    return [], [], [], ""
