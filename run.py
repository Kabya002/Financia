try:    
    from flask import Flask, render_template, redirect, url_for, request, flash,jsonify,session
    import uuid
    from flask_bootstrap import Bootstrap
    from flask_wtf import CSRFProtect
    from flask_wtf.csrf import CSRFError
    from datetime import datetime
    from functools import wraps
    from werkzeug.security import generate_password_hash, check_password_hash
    from flask_gravatar import Gravatar  # type: ignore
    from app.forms import (IncomeForm, RegisterForm, LoginForm, ExpenseForm, ContactForm)
    from app.models import (User, Income, Expense, Category)
    from app.utils import (get_total_income,get_total_expense,get_balance,get_monthly_expense,get_weekly_expense, get_chart_data_for_period)
    from app import create_app
    from app.routes.auth import (auth_bp)
    from app.routes.dashboard import (dashboard_bp)
    from datetime import date, timedelta
    import smtplib
    import os
    from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
    import requests 
    from werkzeug.utils import secure_filename
    from itertools import chain
    from dotenv import load_dotenv
except ImportError as e:
    print("Required libraries are not installed. Please run 'pip install -r requirements.txt'.")
    raise e

load_dotenv()
app = create_app()

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'True') == 'True')


