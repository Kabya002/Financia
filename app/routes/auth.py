from flask import (Blueprint, render_template, redirect, url_for, request, jsonify, make_response)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (create_access_token, unset_jwt_cookies, set_access_cookies, jwt_required, get_jwt)
from app.models import User
from app.extensions import db, jwt_blacklist,jwt
from app.forms import RegisterForm, LoginForm
import logging

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
logger = logging.getLogger(__name__)

# Register Route
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        existing_user = db.session.query(User).filter_by(email=form.email.data).first()
        if existing_user:
            return redirect(url_for("auth.login", msg="Email already registered. Please log in.", category="danger"))

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()

        access_token = create_access_token(identity=new_user.id)
        response = redirect(url_for("dashboard.dashboard", msg="Registration successful!", category="success"))
        set_access_cookies(response, access_token)
        return response

    if request.method == "POST":
        logger.warning(f"Registration failed: {form.errors}")
        return render_template("register.html", form=form, msg="Please fix the errors.", category="danger")

    return render_template("register.html", form=form)

# Login Route
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.query(User).filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            access_token = create_access_token(identity=user.id)
            response = redirect(url_for("dashboard.dashboard", msg="Logged in successfully!", category="success"))
            set_access_cookies(response, access_token)
            return response
        return redirect(url_for("auth.login", msg="Invalid email or password.", category="danger"))

    if request.method == "POST":
        logger.warning(f"Login failed: {form.errors}")
        return render_template("login.html", form=form, msg="Please fix the errors.", category="danger")

    return render_template("login.html", form=form)

# Logout Route
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    jwt_blacklist.add(jti)

    response = redirect(url_for("auth.login", msg="Logged out successfully.", category="success"))
    unset_jwt_cookies(response)
    return response

