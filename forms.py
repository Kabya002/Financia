from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, SubmitField, PasswordField, DateField
from wtforms.validators import DataRequired, Email, InputRequired,Length, EqualTo

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email(message="Enter a valid email address!")])
    password = PasswordField("Password", validators=[
        DataRequired(), 
        Length(min=6, message="Password must be at least 6 characters")
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match!")
    ])
    submit = SubmitField("Sign Up")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")
    
class ExpenseForm(FlaskForm):
    category = StringField("Expense Category", validators=[DataRequired()])
    amount = FloatField("Amount", validators=[DataRequired()])
    date = DateField("Date", validators=[DataRequired()])
    submit = SubmitField("Add Expense")


class IncomeForm(FlaskForm):
    category = StringField("Income Category", validators=[DataRequired()])
    amount = FloatField("Amount", validators=[DataRequired()])
    date = DateField("Date", validators=[DataRequired()])
    submit = SubmitField("Add Income")


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    message = StringField("Message", validators=[DataRequired()])
    submit = SubmitField("Send Message")