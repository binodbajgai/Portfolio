from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.file import FileField, FileAllowed

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



# ==========================================
# Project Form
# ==========================================

class ProjectForm(FlaskForm):

    title = StringField(
        "Title",
        validators=[
            DataRequired(),
            Length(max=150)
        ]
    )

    subtitle = StringField(
        "Subtitle",
        validators=[
            Length(max=150)
        ]
    )

    description = TextAreaField(
        "Description",
        validators=[
            DataRequired()
        ]
    )

    image = FileField(
    "Project Image",
    validators=[
        FileAllowed(
            ["jpg", "jpeg", "png", "webp"],
            "Images only!"
        )
    ]
)

    github = StringField(
        "GitHub URL",
        validators=[
            Length(max=255)
        ]
    )

    demo = StringField(
        "Live Demo URL",
        validators=[
            Length(max=255)
        ]
    )

    tech = StringField(
        "Technologies (comma separated)"
    )

    submit = SubmitField("Save Project")


    