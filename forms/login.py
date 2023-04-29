from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, TextAreaField, SubmitField, EmailField, SelectField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    type = SelectField('Тип учетной записи', choices=[('dispatcher', 'Диспетчер'), ('customer', 'Заказчик')])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('АВТОРИЗОВАТЬСЯ')