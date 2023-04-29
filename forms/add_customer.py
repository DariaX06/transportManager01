from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, TelField
from wtforms.validators import DataRequired


class AddCustomerForm(FlaskForm):
    name = StringField('ФИО', validators=[DataRequired()])
    job_title = StringField('Должность', validators=[DataRequired()])
    tel = TelField('Номер телефона')
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('ДОБАВИТЬ СОТРУДНИКА')