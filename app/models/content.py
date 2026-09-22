from ..database import db


class Profile(db.Model):
    __tablename__ = "profile"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(150))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(80))
    github = db.Column(db.String(255))
    linkedin = db.Column(db.String(255))
    roles = db.Column(db.Text)
    photo = db.Column(db.String(255))


class SiteSettings(db.Model):
    __tablename__ = "site_settings"

    id = db.Column(db.Integer, primary_key=True)
    hero_greeting = db.Column(db.String(150), nullable=False)
    projects_stat = db.Column(db.String(50), nullable=False)
    technologies_stat = db.Column(db.String(50), nullable=False)
    journey_stat = db.Column(db.String(50), nullable=False)
    projects_heading = db.Column(db.String(200), nullable=False)
    projects_description = db.Column(db.Text, nullable=False)
    about_achievement = db.Column(db.String(255), nullable=False)
    about_projects = db.Column(db.String(255), nullable=False)
    skills_heading = db.Column(db.String(200), nullable=False)
    skills_description = db.Column(db.Text, nullable=False)
    experience_heading = db.Column(db.String(200), nullable=False)
    experience_description = db.Column(db.Text, nullable=False)
    contact_heading = db.Column(db.String(200), nullable=False)
    contact_description = db.Column(db.Text, nullable=False)


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)


class TimelineEntry(db.Model):
    __tablename__ = "timeline_entries"

    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(20), nullable=False, default="experience")
    year = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    organization = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)
