from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, Email

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
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