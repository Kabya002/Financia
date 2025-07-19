from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.forms import (IncomeForm, RegisterForm, LoginForm, ExpenseForm, ContactForm)
from app.models import (User, Income, Expense, Category)
from app.utils import (get_total_income,get_total_expense,get_balance,get_monthly_expense,get_weekly_expense, get_chart_data_for_period)
from app.extensions import db, logger
from itertools import chain
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid

dashboard_bp = Blueprint('dashboard', __name__, url_prefix="/api/dashboard")

@dashboard_bp.route('/dashboard_route', methods=["GET", "POST"])
@jwt_required()
def dashboard():
    user_id = get_jwt_identity()
    current_user = db.session.get(User, user_id)
    
    expense_form = ExpenseForm()
    income_form = IncomeForm()

    if "submit_expense" in request.form and expense_form.validate_on_submit():
        # Handle expense form
        category_name = expense_form.category.data.strip()
        category = db.session.query(Category).filter_by(name=category_name, user_id=current_user.id).first()
        if not category:
            category = Category(name=category_name, user_id=current_user.id)
            db.session.add(category)
            db.session.commit()

        new_expense = Expense(
            source=category_name,
            date=expense_form.date.data,
            expense=expense_form.amount.data,
            user_id=current_user.id
        )
        db.session.add(new_expense)
        db.session.commit()
        return redirect(url_for('dashboard.dashboard', msg="Expense added successfully!", category="success"))

    elif "submit_income" in request.form and income_form.validate_on_submit():
        # Handle income form
        category_name = income_form.category.data.strip()
        category = db.session.query(Category).filter_by(name=category_name, user_id=current_user.id).first()
        if not category:
            category = Category(name=category_name, user_id=current_user.id)
            db.session.add(category)
            db.session.commit()

        new_income = Income(
            source=category_name,
            date=income_form.date.data,
            income=income_form.amount.data,
            user_id=current_user.id
        )
        db.session.add(new_income)
        db.session.commit()
        return redirect(url_for('dashboard.dashboard', msg="Income added successfully!", category="success"))

    # Load categories and transactions
    expenses = db.session.query(Expense).filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    incomes = db.session.query(Income).filter_by(user_id=current_user.id).order_by(Income.date.desc()).all()
    user_categories = db.session.query(Category).filter_by(user_id=current_user.id).all()

    # Merge income + expense for transaction history
    transactions = sorted(
        chain(
            [{"date": e.date, "source": e.source, "amount": -e.expense} for e in expenses],
            [{"date": i.date, "source": i.source, "amount": i.income} for i in incomes]
        ),
        key=lambda x: x["date"],
        reverse=True
    )

    # Totals and summaries
    total_income = get_total_income(db, current_user.id)
    total_expense = get_total_expense(db, current_user.id)
    total_balance = get_balance(db, current_user.id)
    monthly_expenses = get_monthly_expense(db, current_user.id)
    weekly_expenses = get_weekly_expense(db, current_user.id)

    # Chart data
    chart_type = request.args.get("type", "monthly")
    offset = int(request.args.get("offset", 0))
    labels, income_chart_data, expense_chart_data, range_label = get_chart_data_for_period(
        db, current_user.id, chart_type, offset
    )

    return render_template(
        "dashboard.html",
        expense_form=expense_form,
        income_form=income_form,
        expenses=expenses,
        incomes=incomes,
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        total_balance=total_balance,
        monthly_expenses=monthly_expenses,
        weekly_expenses=weekly_expenses,
        user_categories=user_categories,
        chart_labels=labels,
        chart_income=income_chart_data,
        chart_expense=expense_chart_data,
        chart_range_label=range_label
    )

@dashboard_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    current_user = db.session.get(User, user_id)
    
    chart_data = get_chart_data_for_period(db, current_user.id, 'month', 0)
    total_income = get_total_income(db, current_user.id)
    total_expense = get_total_expense(db, current_user.id)
    total_balance = total_income - total_expense
    start_of_month = datetime(datetime.today().year, datetime.today().month, 1)
    member_since = current_user.created_at
    monthly_entries = db.session.query(Expense).filter(Expense.user_id == current_user.id, Expense.date >= start_of_month).count()

    achievements = []
    if total_income >= 10000:
        achievements.append("🎯 Earned ₹10K+ Income")
    if total_expense >= 5000:
        achievements.append("💸 Spent ₹5K+")
    if total_balance >= 5000:
        achievements.append("🏆 Saved ₹5K+")
    if len(current_user.expenses) >= 30:
        achievements.append("📅 Logged 30+ Expenses")
    if len(current_user.incomes) >= 30:
        achievements.append("💼 Logged 30+ Incomes")
    if monthly_entries >= 5:
        achievements.append("📅 Logged 5+ Expenses This Month")
    return render_template(
        "profile.html",
        current_user= current_user,
        total_income=total_income,
        total_expense=total_expense,
        total_balance=total_balance,
        chart_data=chart_data,
        achievements=achievements,
        member_since=member_since.strftime('%b %d, %Y'),
        monthly_entries=monthly_entries
    )

@dashboard_bp.route("/account-settings", methods=["GET", "POST"])
@jwt_required()
def account_settings():
    user_id = get_jwt_identity()
    current_user = db.session.get(User, user_id)
    form = RegisterForm(obj=current_user)

    # handles GET: just render the form with user data
    if request.method == "GET":
        return render_template("account.html", form=form)

    # Handles POST
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.commit()
        return redirect(url_for('dashboard.account_settings', msg="Account settings updated successfully!", category="success"))
    
    # POST failed (form invalid), redisplay form with errors
    return render_template("account.html", form=form)

@dashboard_bp.route("/upload-images", methods=["POST"])
@jwt_required()
def upload_images():
    user_id = get_jwt_identity()
    current_user = db.session.get(User, user_id)

    allowed_exts = {"jpg", "jpeg", "png", "gif", "webp"}

    def delete_if_custom(file_path: str):
        if os.path.exists(file_path) and "default-" not in file_path:
            os.remove(file_path)

    # Profile Picture 
    profile_file = request.files.get("profile_picture")
    if profile_file and profile_file.filename != "":
        if "." not in profile_file.filename:
            logger.warning(f"Rejected upload: no extension in profile picture for user {user_id}")
            return redirect(url_for("dashboard.account_settings", msg="Invalid profile image file type.", category="danger"))

        profile_ext = secure_filename(profile_file.filename).rsplit(".", 1)[-1].lower()
        if profile_ext not in allowed_exts:
            logger.warning(f"Rejected upload: invalid extension '{profile_ext}' for profile picture of user {user_id}")
            return redirect(url_for("dashboard.account_settings", msg="Invalid profile image file type.", category="danger"))

        profile_filename = f"{uuid.uuid4().hex}.{profile_ext}"
        profile_dir = os.path.join("static", "uploads")
        os.makedirs(profile_dir, exist_ok=True)
        profile_path = os.path.join(profile_dir, profile_filename)

        # Delete old profile image if needed
        old_profile_path = os.path.join("static", current_user.profile_image_url.split("static/")[-1])
        delete_if_custom(old_profile_path)

        profile_file.save(profile_path)
        current_user.profile_image_url = f"static/uploads/{profile_filename}"

    # Banner Image 
    banner_file = request.files.get("banner_image")
    if banner_file and banner_file.filename != "":
        if "." not in banner_file.filename:
            logger.warning(f"Rejected upload: no extension in banner image for user {user_id}")
            return redirect(url_for("dashboard.account_settings", msg="Invalid banner image file type.", category="danger"))

        banner_ext = secure_filename(banner_file.filename).rsplit(".", 1)[-1].lower()
        if banner_ext not in allowed_exts:
            logger.warning(f"Rejected upload: invalid extension '{banner_ext}' for banner image of user {user_id}")
            return redirect(url_for("dashboard.account_settings", msg="Invalid banner image file type.", category="danger"))

        banner_filename = f"{uuid.uuid4().hex}.{banner_ext}"
        banner_dir = os.path.join("static", "banners")
        os.makedirs(banner_dir, exist_ok=True)
        banner_path = os.path.join(banner_dir, banner_filename)

        # Delete old banner image if needed
        old_banner_path = os.path.join("static", current_user.banner_image_url.split("static/")[-1])
        delete_if_custom(old_banner_path)

        banner_file.save(banner_path)
        current_user.banner_image_url = f"static/banners/{banner_filename}"

    db.session.commit()
    return redirect(url_for("dashboard.profile", msg="Images uploaded successfully!", category="success"))

@dashboard_bp.route("/edit-profile", methods=["GET", "POST"])
@jwt_required()
def edit_profile():
    user_id = get_jwt_identity()
    current_user = db.session.get(User, user_id)
    form = RegisterForm(obj=current_user)
    if request.method == "GET":
        return render_template("edit_profile.html", form=form, msg="Please fix the errors.", category="warning")

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.commit()
    return redirect(url_for('dashboard.account_settings', msg="Profile updated successfully!", category="success"))

@dashboard_bp.route("/change-password", methods=["GET", "POST"])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    current_user = db.session.get(User, user_id)
    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not check_password_hash(current_user.password, current_password):
            return redirect(url_for("dashboard.change_password", msg="Current password is incorrect.", category="danger"))
        elif new_password != confirm_password:
            return redirect(url_for("dashboard.change_password", msg="Passwords do not match.", category="warning"))
        else:
            current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)
            db.session.commit()
            return redirect(url_for('dashboard.account_settings', msg="Password updated successfully.", category="success"))

@dashboard_bp.route("/delete-account", methods=["POST"])
@jwt_required()
def delete_account():
    user_id = get_jwt_identity()
    current_user = db.session.get(User, user_id)
    # Delete related data
    db.session.query(Income).filter_by(user_id=current_user.id).delete()
    db.session.query(Expense).filter_by(user_id=current_user.id).delete()
    db.session.query(Category).filter_by(user_id=current_user.id).delete()

    # Delete the user
    db.session.delete(current_user)
    db.session.commit()
    return redirect(url_for('home', msg="Account deleted successfully.", category="success"))

@dashboard_bp.route("/api/chart-data")
@jwt_required()
def chart_data():
    user_id = get_jwt_identity()
    current_user = db.session.get(User, user_id)
    chart_type = request.args.get("type", "month")
    offset = int(request.args.get("offset", 0))

    # Ensure chart_type is valid
    if chart_type not in ("month", "week"):
        return jsonify({"error": "Invalid chart type"}), 400

    # Get chart data for that user
    labels, income_data, expense_data, range_label = get_chart_data_for_period(
        db, current_user.id, chart_type, offset
    )

    return jsonify({
        "labels": labels,
        "income": income_data,
        "expense": expense_data,
        "range_label": range_label
    })
