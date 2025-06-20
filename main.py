from flask import Flask, render_template, redirect, url_for, request, abort, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, DateTime
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
#from flask_ckeditor import CKEditor, CKEditorField
from datetime import datetime
#from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from forms import IncomeForm, RegisterForm, LoginForm, ExpenseForm, ContactForm
from config import Config
from models import User, Income, Expense, Category, Base
from flask import session
from utils import (get_total_income,get_total_expense,get_balance,get_monthly_expense,get_weekly_expense, get_chart_data_for_period)
from datetime import date, timedelta
import smtplib
import os
from flask import jsonify
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
bootstrap = Bootstrap5(app)
csrf_token = CSRFProtect(app)


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash("CSRF token missing or incorrect.", "danger")
    return redirect(request.referrer or url_for('dashboard'))

with app.app_context():
    Base.metadata.create_all(bind=db.engine)

gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.context_processor
def inject_request():
    return dict(request=request)

@app.route('/')
def home():
    return render_template("home.html")


@app.route('/dashboard', methods=["GET", "POST"])
@login_required
def dashboard():
    expense_form = ExpenseForm()
    income_form = IncomeForm()

    #Handle Expense Form Submission
    if expense_form.validate_on_submit() and expense_form.submit.data:
        category_name = expense_form.category.data.strip()

        # Save new category if it doesn't exist
        category = db.session.query(Category).filter_by(name=category_name, user_id=current_user.id).first()
        if not category:
            category = Category(name=category_name, user_id=current_user.id)
            db.session.add(category)
            db.session.commit()

        # Save new expense
        new_expense = Expense(
            source=category_name,
            date=expense_form.date.data,  # This is already a datetime.date object from the WTForm
            expense=expense_form.amount.data,
            user_id=current_user.id
        )

        db.session.add(new_expense)
        db.session.commit()
        flash("Expense added successfully!", "success")
        return redirect(url_for('dashboard'))

    # 💵 Handle Income Form Submission (optional)
    if income_form.validate_on_submit() and income_form.submit.data:
        new_income = Income(
            source=income_form.source.data,
            date=income_form.date.data,
            income=income_form.amount.data,
            user_id=current_user.id
        )

        db.session.add(new_income)
        db.session.commit()
        flash("Income added successfully!", "success")
        return redirect(url_for('dashboard'))

    # 📦 Load expense history & category list
    expenses = db.session.query(Expense).filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    user_categories = db.session.query(Category).filter_by(user_id=current_user.id).all()

    # 📊 Totals using utils
    total_income = get_total_income(db, current_user.id)
    total_expense = get_total_expense(db, current_user.id)
    total_balance = get_balance(db, current_user.id)
    monthly_expenses = get_monthly_expense(db, current_user.id)
    weekly_expenses = get_weekly_expense(db, current_user.id)
    
  #Chart data: Get last 3 periods (month or week)
    chart_type = request.args.get("type", "monthly")
    offset = int(request.args.get("offset", 0))
    labels, income_chart_data, expense_chart_data, range_label = get_chart_data_for_period(db, current_user.id, chart_type, offset)
    return render_template(
    "dashboard.html",
    expense_form=expense_form,
    income_form=income_form,
    expenses=expenses,
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


@app.route("/api/chart-data")
@login_required
def chart_data():
    chart_type = request.args.get("type", "month")  # 'month' or 'week'
    offset = int(request.args.get("offset", 0))
    
    chart_data = get_chart_data_for_period(db, current_user.id, chart_type, offset)
    return jsonify(chart_data)

@login_required
@app.route('/income')
def income():
    return render_template("income.html")


@app.route("/account-settings", methods=["GET", "POST"])
@login_required
def account_settings():
    form = RegisterForm(obj=current_user)  # Prefill with current user data

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for('account_settings'))

    return render_template("account.html", form=form)


@app.route('/profile')
@login_required
def profile():
    chart_data= get_chart_data_for_period(db, current_user.id, 'month', 0)
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
        user=current_user,
        total_income=total_income,
        total_expense=total_expense,
        total_balance=total_balance,
        chart_data=chart_data,
        achievements=achievements,
        member_since=member_since.strftime('%b %d, %Y'),
        monthly_entries=monthly_entries
    )
    

@app.route("/upload-images", methods=["POST"])
@login_required
def upload_images():
    allowed_exts = ["jpg", "jpeg", "png", "gif", "webp"]

    def delete_if_custom(file_path: str):
        # Only delete if file exists and is not a default image
        if os.path.exists(file_path) and "default-" not in file_path:
            os.remove(file_path)

    # --- Handle Profile Picture ---
    profile_file = request.files.get("profile_picture")
    if profile_file and profile_file.filename != "":
        profile_ext = secure_filename(profile_file.filename).rsplit(".", 1)[-1].lower()
        if profile_ext in allowed_exts:
            profile_filename = f"{uuid.uuid4().hex}.{profile_ext}"
            profile_dir = os.path.join("static", "uploads")
            os.makedirs(profile_dir, exist_ok=True)
            profile_path = os.path.join(profile_dir, profile_filename)

            # Delete old profile image
            old_profile_path = os.path.join("static", current_user.profile_image_url.split("static/")[-1])
            delete_if_custom(old_profile_path)

            profile_file.save(profile_path)
            current_user.profile_image_url = f"static/uploads/{profile_filename}"
        else:
            flash("Invalid profile image file type.", "danger")

    # --- Handle Banner Image ---
    banner_file = request.files.get("banner_image")
    if banner_file and banner_file.filename != "":
        banner_ext = secure_filename(banner_file.filename).rsplit(".", 1)[-1].lower()
        if banner_ext in allowed_exts:
            banner_filename = f"{uuid.uuid4().hex}.{banner_ext}"
            banner_dir = os.path.join("static", "banners")
            os.makedirs(banner_dir, exist_ok=True)
            banner_path = os.path.join(banner_dir, banner_filename)

            # Delete old banner image
            old_banner_path = os.path.join("static", current_user.banner_image_url.split("static/")[-1])
            delete_if_custom(old_banner_path)

            banner_file.save(banner_path)
            current_user.banner_image_url = f"static/banners/{banner_filename}"
        else:
            flash("Invalid banner image file type.", "danger")

    db.session.commit()
    flash("Images updated successfully!", "success")
    return redirect(url_for("profile"))

@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = RegisterForm(obj=current_user)  # reuse your RegisterForm
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Profile updated successfully.", "success")
    return redirect(url_for('account_settings'))


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not check_password_hash(current_user.password, current_password):
            flash("Current password is incorrect.", "danger")
        elif new_password != confirm_password:
            flash("Passwords do not match.", "warning")
        else:
            current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)
            db.session.commit()
            flash("Password updated successfully.", "success")
        return redirect(url_for('account_settings'))

@app.route("/delete-account", methods=["POST"])
@login_required
def delete_account():
    # Delete related data
    db.session.query(Income).filter_by(user_id=current_user.id).delete()
    db.session.query(Expense).filter_by(user_id=current_user.id).delete()
    db.session.query(Category).filter_by(user_id=current_user.id).delete()

    # Delete the user
    db.session.delete(current_user)
    db.session.commit()
    flash("Your account has been deleted.", "danger")
    return redirect(url_for('home'))

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar_one_or_none()
        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for('login'))

        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash("Registered successfully!", "success")
        return redirect(url_for('dashboard'))
    else:
        if request.method == "POST":
            print("Form errors:", form.errors) 
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar_one_or_none()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password!", "danger")
    else:
        if request.method == "POST":
            print("Form errors:", form.errors) 
    return render_template("login.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You’ve been logged out.", "info")
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)

