from ..database import db


class Project(db.Model):

    __tablename__ = "projects"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    subtitle = db.Column(
        db.String(150)
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    image = db.Column(
        db.String(255)
    )

    github = db.Column(
        db.String(255)
    )

    demo = db.Column(
        db.String(255)
    )

    tech = db.Column(
        db.Text
    )