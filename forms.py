from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, DateField, BooleanField
from wtforms.validators import DataRequired, Email
from datetime import datetime


class RegisterForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()])
    email = EmailField("Email:", validators=[DataRequired(), Email()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    email = EmailField("Email:", validators=[DataRequired(), Email()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Submit")


class CreateForm(FlaskForm):
    name = StringField("Title", validators=[DataRequired()])
    date = DateField("Date", default=datetime.now())
    task1 = StringField("Task 1", validators=[DataRequired()])
    task2 = StringField("Task 2")
    task3 = StringField("Task 3")
    task4 = StringField("Task 4")
    task5 = StringField("Task 5")
    task6 = StringField("Task 6")
    task7 = StringField("Task 7")
    task8 = StringField("Task 8")
    task9 = StringField("Task 9")
    task10 = StringField("Task 10")
    submit = SubmitField("Submit")


class TasksField(FlaskForm):
    ta = BooleanField("Does the cafe have sockets?")
                    
