from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextField
from wtforms.validators import DataRequired


class CabinetForm(FlaskForm):
    surname = StringField('Фамилия пользователя', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    how_to_contact = TextField('Как с Вами связаться')
    submit = SubmitField('Отправить')
