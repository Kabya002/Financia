from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, Email, InputRequired,Length, EqualTo

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    username = StringField("Name", validators=[InputRequired(), Length(min=2, max=30)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")
    
class IncomeForm(FlaskForm):
    source = StringField("Income Source", validators=[DataRequired()])
    date = StringField("Date (YYYY-MM-DD)", validators=[DataRequired()])
    income = FloatField("Income", validators=[DataRequired()])
    submit = SubmitField("Add Income")

class ExpenseForm(FlaskForm):
    source = StringField("Expense Source", validators=[DataRequired()])
    date = StringField("Date (YYYY-MM-DD)", validators=[DataRequired()])
    expanse = FloatField("Expense", validators=[DataRequired()])
    submit = SubmitField("Add Expense")

class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    message = StringField("Message", validators=[DataRequired()])
    submit = SubmitField("Send Message")