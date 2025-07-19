from flask import Flask, redirect, request, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config
from app.extensions import db, jwt_blacklist, csrf_token, jwt, bootstrap
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, create_access_token, unset_jwt_cookies, set_access_cookies
from app.forms import (IncomeForm, RegisterForm, LoginForm, ExpenseForm, ContactForm)
from app.models import (User, Income, Expense, Category, TokenBlocklist)
from app.utils import (get_total_income,get_total_expense,get_balance,get_monthly_expense,get_weekly_expense, get_chart_data_for_period)
from app.routes.auth import (auth_bp)
from app.routes.dashboard import (dashboard_bp)
from logging.handlers import RotatingFileHandler
from flask_wtf.csrf import CSRFError
from dotenv import load_dotenv
import traceback
import datetime
import logging
import os

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # JWT config
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"
    app.config["JWT_COOKIE_SECURE"] = os.getenv("FLASK_ENV") == "development"
    app.config["JWT_COOKIE_SAMESITE"] = "Lax"
    app.config["JWT_COOKIE_CSRF_PROTECT"] = True
    #app.config["FLASK_DEBUG"] = os.getenv("FLASK_DEBUG", "False") == "True"
    #app.config["JWT_COOKIE_SECURE"] = os.getenv("JWT_COOKIE_SECURE", "False") == "True"

    # Init extensions
    db.init_app(app)
    csrf_token.init_app(app)
    jwt.init_app(app)
    bootstrap.init_app(app)

    # Token blacklist check
    from app.models import TokenBlocklist
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return db.session.query(TokenBlocklist.id).filter_by(jti=jwt_payload["jti"]).scalar() is not None

    # CSRF error handler
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return redirect(url_for('dashboard.dashboard', msg="CSRF token missing or incorrect.", category="danger"))

    # Context processor for templates
    @app.context_processor
    def inject_globals():
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id) if user_id else None
        except Exception:
            traceback.print_exc() if app.config["DEBUG"] else None
            user = None
        return dict(current_user=user, request=request)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    # Home route
    @app.route('/')
    def home():
        return render_template("home.html")
    
    # Logging setup 
    if not os.path.exists("logs"):
        os.makedirs("logs")

    file_handler = RotatingFileHandler("logs/app.log", maxBytes=10240, backupCount=3)
    file_handler.setFormatter(logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    ))

    if app.config["FLASK_ENV"] == "development":
        file_handler.setLevel(logging.WARNING)
        app.logger.setLevel(logging.WARNING)
    else:
        file_handler.setLevel(logging.DEBUG)
        app.logger.setLevel(logging.DEBUG)

    app.logger.addHandler(file_handler)
    app.logger.info("App startup")
    
    # Error handlers
    @jwt.expired_token_loader
    def handle_expired_token(jwt_header, jwt_payload):
        response = redirect(url_for("auth.login", msg="Session expired. Please log in again.", category="warning"))
        unset_jwt_cookies(response)
        return response

    @jwt.invalid_token_loader
    def handle_invalid_token(reason):
        response = redirect(url_for("auth.login", msg="Invalid session token.", category="danger"))
        unset_jwt_cookies(response)
        return response

    @jwt.unauthorized_loader
    def handle_missing_token(reason):
        return redirect(url_for("auth.login", msg="Please log in to continue.", category="warning"))

    @jwt.needs_fresh_token_loader
    def handle_fresh_token_required(jwt_header, jwt_payload):
        return redirect(url_for("auth.login", msg="Reauthentication required.", category="warning"))
    
    if app.config["FLASK_ENV"] == "development":
        with app.app_context():
            db.create_all()
    return app
