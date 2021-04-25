from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class ChatForm(FlaskForm):
    message = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Подтвердить')
