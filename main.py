from flask import Flask, render_template, redirect, url_for, request, abort, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, DateTime
from flask_wtf import CSRFProtect
#from flask_ckeditor import CKEditor, CKEditorField
from datetime import datetime
#from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from forms import IncomeForm, RegisterForm, LoginForm, ExpenseForm, ContactForm
from config import Config
from models import User, Income, Expense
from utils import is_valid_amount, format_currency, get_current_date
import smtplib
import os


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)

with app.app_context():
    db.create_all()

gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template("home.html")

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")

@login_required
@app.route('/income')
def income():
    return render_template("income.html")

@login_required
@app.route('/profile')
def profile():
    return render_template("profile.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for('login'))
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        new_user = User(
            email=form.email.data,
            password=hashed_password,
            name=form.username.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please log in!", "success")
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "danger")
    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You’ve been logged out.", "info")
    return redirect(url_for('home'))





if __name__ == '__main__':
    app.run(debug=True)

