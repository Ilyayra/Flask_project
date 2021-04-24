from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class JobForm(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired()])
    description = TextAreaField('Описание')
    pay = IntegerField('Оплата в рублях', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')
