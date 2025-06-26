from models import Income, Expense
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime, timedelta,date
from collections import defaultdict
from dateutil.relativedelta import relativedelta
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



def get_chart_data_for_period(db, user_id, chart_type, offset=0):
    if chart_type == "week":
        # 🗓️ Get current week start (Monday)
        today = datetime.today().date()
        start_of_week = today - timedelta(days=today.weekday()) - timedelta(weeks=offset)
        end_of_week = start_of_week + timedelta(days=6)

        # Initialize totals for each day
        labels = [(start_of_week + timedelta(days=i)).strftime("%a") for i in range(7)]
        income_totals = [0] * 7
        expense_totals = [0] * 7

        # Query transactions in week
        incomes = db.session.query(Income).filter(
            Income.user_id == user_id,
            Income.date >= start_of_week,
            Income.date <= end_of_week
        ).all()

        expenses = db.session.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.date >= start_of_week,
            Expense.date <= end_of_week
        ).all()

        for i in incomes:
            day_index = (i.date - start_of_week).days
            income_totals[day_index] += i.income

        for e in expenses:
            day_index = (e.date - start_of_week).days
            expense_totals[day_index] += e.expense

        range_label = f"{start_of_week.strftime('%d %b')} - {end_of_week.strftime('%d %b')}"
        return labels, income_totals, expense_totals, range_label

    elif chart_type == "month":
        # 📅 Get current month minus offset
        target_month = datetime.today().replace(day=1) - relativedelta(months=offset)
        month_label = target_month.strftime("%B %Y")
        labels = []
        income_totals = []
        expense_totals = []

        for i in range(3):  # current + last 2 months
            month = target_month - relativedelta(months=i)
            start_date = month.replace(day=1)
            end_date = (start_date + relativedelta(months=1)) - timedelta(days=1)
            label = month.strftime("%b")

            income = db.session.query(Income).filter(
                Income.user_id == user_id,
                Income.date >= start_date,
                Income.date <= end_date
            ).all()
            expense = db.session.query(Expense).filter(
                Expense.user_id == user_id,
                Expense.date >= start_date,
                Expense.date <= end_date
            ).all()

            labels.insert(0, label)
            income_totals.insert(0, sum(i.income for i in income))
            expense_totals.insert(0, sum(e.expense for e in expense))

        range_label = f"{labels[0]} - {labels[-1]}"
        return labels, income_totals, expense_totals, range_label

    return [], [], [], ""
# This code is a utility module for a Flask application that handles financial data.
# It provides functions to calculate total income, total expenses, balance, monthly and weekly expenses,