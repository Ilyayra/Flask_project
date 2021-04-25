from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, DateTimeField, TextField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
import datetime


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    repeat_password = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия пользователя', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    how_to_contact = TextField('Как с Вами связаться')
    create_date = DateTimeField(default=datetime.datetime.now)
    submit = SubmitField('Отправить')
