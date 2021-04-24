from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class SellForm(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired()])
    description = TextAreaField('Описание')
    price = IntegerField('Цена', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')
