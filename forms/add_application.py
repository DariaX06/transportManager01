from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired


class AddApplicationForm(FlaskForm):
    task = TextAreaField("Задача", validators=[DataRequired()])
    start = DateField('Начальная дата', format='%Y-%m-%d')
    end = DateField('Конечная дата', format='%Y-%m-%d')
    transport_id = SelectField('Транспорт', choices=[])

    submit = SubmitField('ОФОРМИТЬ ЗАЯВКУ')