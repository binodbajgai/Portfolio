from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length


class ContactForm(FlaskForm):

    name = StringField(
        "Name",
        validators=[
            DataRequired(),
            Length(min=2, max=100)
        ]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    subject = StringField(
        "Subject",
        validators=[
            DataRequired(),
            Length(max=150)
        ]
    )

    message = TextAreaField(
        "Message",
        validators=[
            DataRequired(),
            Length(min=10)
        ]
    )

    submit = SubmitField("Send Message")

    # ==========================================
# Admin Login Form
# ==========================================

class AdminLoginForm(FlaskForm):

    username = StringField(
        "Username",
        validators=[DataRequired()]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired()]
    )

    submit = SubmitField("Login")