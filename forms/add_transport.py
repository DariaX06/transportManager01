from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class AddTransportForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    coordinates = StringField('Координаты', validators=[DataRequired()])
    state = BooleanField("Исправность")
    submit = SubmitField('ДОБАВИТЬ ТРАНСПОРТ')