from PIL import Image, UnidentifiedImageError

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired

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
# Admin Login Forms 
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


class CVUploadForm(FlaskForm):

    cv = FileField(
        "Upload CV",
        validators=[
            FileRequired(message="Please choose a PDF to upload."),
            FileAllowed(
                ["pdf"],
                "PDF files only!"
            )
        ]
    )

    def validate_cv(self, field):

        if not field.data or not getattr(field.data, "filename", ""):
            return

        filename = field.data.filename.lower()

        if not filename.endswith(".pdf"):
            raise ValidationError("Upload a valid PDF file.")

        stream = field.data.stream
        position = stream.tell()

        try:
            stream.seek(0)
            if stream.read(5) != b"%PDF-":
                raise ValidationError("Upload a valid PDF file.")
        finally:
            stream.seek(position)

    submit = SubmitField("Upload CV")


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

    def validate_image(self, field):

        if not field.data or not getattr(field.data, "filename", ""):
            return

        stream = field.data.stream
        position = stream.tell()

        try:
            stream.seek(0)
            with Image.open(stream) as image:
                image.verify()

                if (image.format or "").upper() not in {"JPEG", "PNG", "WEBP"}:
                    raise ValidationError("Upload a valid JPEG, PNG, or WEBP image.")

        except (UnidentifiedImageError, OSError):
            raise ValidationError("Upload a valid image file.")

        finally:
            stream.seek(position)

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


class ProfileForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=150)])
    title = StringField("Professional title", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Introduction", validators=[DataRequired()])
    location = StringField("Location", validators=[Length(max=150)])
    email = StringField("Email", validators=[Email(), Length(max=255)])
    phone = StringField("Phone", validators=[Length(max=80)])
    github = StringField("GitHub URL", validators=[Length(max=255)])
    linkedin = StringField("LinkedIn URL", validators=[Length(max=255)])
    roles = StringField("Roles (comma separated)", validators=[Length(max=500)])
    photo = FileField("Profile photo", validators=[FileAllowed(["jpg", "jpeg", "png", "webp"], "Images only!")])
    submit = SubmitField("Save profile")


class SiteSettingsForm(FlaskForm):
    hero_greeting = StringField("Hero greeting", validators=[DataRequired(), Length(max=150)])
    projects_stat = StringField("Projects stat", validators=[DataRequired(), Length(max=50)])
    technologies_stat = StringField("Technologies stat", validators=[DataRequired(), Length(max=50)])
    journey_stat = StringField("Journey stat", validators=[DataRequired(), Length(max=50)])
    projects_heading = StringField("Projects heading", validators=[DataRequired(), Length(max=200)])
    projects_description = TextAreaField("Projects description", validators=[DataRequired()])
    about_achievement = StringField("About achievement text", validators=[DataRequired(), Length(max=255)])
    about_projects = StringField("About projects text", validators=[DataRequired(), Length(max=255)])
    skills_heading = StringField("Skills heading", validators=[DataRequired(), Length(max=200)])
    skills_description = TextAreaField("Skills description", validators=[DataRequired()])
    experience_heading = StringField("Timeline heading", validators=[DataRequired(), Length(max=200)])
    experience_description = TextAreaField("Timeline description", validators=[DataRequired()])
    contact_heading = StringField("Contact heading", validators=[DataRequired(), Length(max=200)])
    contact_description = TextAreaField("Contact description", validators=[DataRequired()])
    submit = SubmitField("Save site copy")


class SkillForm(FlaskForm):
    name = StringField("Skill name", validators=[DataRequired(), Length(max=100)])
    icon = StringField("Font Awesome icon class", validators=[DataRequired(), Length(max=150)])
    description = StringField("Description", validators=[DataRequired(), Length(max=255)])
    position = StringField("Display order", validators=[Length(max=10)])
    submit = SubmitField("Save skill")


class TimelineEntryForm(FlaskForm):
    kind = StringField("Type (experience or achievement)", validators=[DataRequired(), Length(max=20)])
    year = StringField("Year or date range", validators=[DataRequired(), Length(max=100)])
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    organization = StringField("Company, school, or organizer", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description", validators=[DataRequired()])
    position = StringField("Display order", validators=[Length(max=10)])
    submit = SubmitField("Save entry")


    
