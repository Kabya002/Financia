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



@app.route('/')
def home():
    return render_template("home.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/income')
def income():
    return render_template("income.html")

@app.route('/profile')
def profile():
    return render_template("profile.html")

@app.route('/register')
def register():
    return render_template("register.html", form=RegisterForm())
    
@app.route('/login')
def login():
    return render_template("login.html", form=LoginForm())

@app.route('/logout')
def logout():
    return redirect(url_for('home'))




if __name__ == '__main__':
    app.run(debug=True)

