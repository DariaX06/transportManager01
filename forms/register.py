from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, TelField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    name = StringField('ФИО', validators=[DataRequired()])
    company = StringField('Компания', validators=[DataRequired()])
    tel = TelField('Номер телефона')
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('ЗАРЕГИСТРИРОВАТЬСЯ')