from datetime import datetime
from flask import flash
import pymysql

# --- DATE HELPERS ---
def get_current_date():
    return datetime.now().strftime('%Y-%m-%d')

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None

# --- VALIDATORS ---
def is_valid_amount(amount):
    try:
        return float(amount) >= 0
    except (ValueError, TypeError):
        return False

def is_valid_category(category, allowed_categories):
    return category in allowed_categories

# --- FORMATTERS ---
def format_currency(amount):
    try:
        return f"₹{float(amount):,.2f}"
    except (ValueError, TypeError):
        return "₹0.00"

# --- SUMMARY FUNCTIONS ---
def calculate_total(transactions):
    return sum(float(txn['amount']) for txn in transactions)

def group_by_category(transactions):
    summary = {}
    for txn in transactions:
        category = txn['category']
        summary[category] = summary.get(category, 0) + float(txn['amount'])
    return summary

# --- BUDGET HELPERS ---
def calculate_remaining_budget(income, total_expenses):
    try:
        return float(income) - float(total_expenses)
    except (ValueError, TypeError):
        return 0.0

def generate_budget_alert(remaining):
    if remaining < 0:
        return "⚠️ Over budget!"
    elif remaining < 1000:
        return "🟡 Budget running low"
    return "🟢 You're within budget"

# --- MYSQL DB HELPERS ---
def execute_query(cursor, query, params=None):
    try:
        cursor.execute(query, params or ())
        return cursor.fetchall()
    except pymysql.MySQLError as e:
        print("Database Error:", e)
        flash("Database error occurred.", "danger")
        return []

def insert_record(cursor, query, params):
    try:
        cursor.execute(query, params)
        return True
    except pymysql.MySQLError as e:
        print("Insert Error:", e)
        flash("Failed to insert record.", "danger")
        return False
