from flask import Blueprint, abort, current_app, render_template, flash, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError

from .database import db
from .models.message import Message
from .portfolio_data import portfolio
from .forms import ContactForm
from .models.project import Project
from .storage import cv_url

main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def home():

    form = ContactForm()

    if form.validate_on_submit():

        new_message = Message(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data
        )

        try:

            db.session.add(new_message)
            db.session.commit()

        except Exception as e:

            db.session.rollback()
            current_app.logger.exception(e)
            raise

        flash(
            "Your message has been sent successfully!",
            "success"
        )

        return redirect(url_for("main.home"))

    db_projects = Project.query.order_by(Project.id.desc()).all()

    # Fall back to static portfolio data when the DB has no projects yet
    if db_projects:
        projects = db_projects
    else:
        projects = []
        for p in portfolio.get("projects", []):
            # Normalize tech: list → comma-separated string (template calls .split(","))
            p = dict(p)
            if isinstance(p.get("tech"), list):
                p["tech"] = ", ".join(p["tech"])
            projects.append(type("Project", (), p)())

    return render_template(
        "index.html",
        portfolio=portfolio,
        form=form,
        projects=projects,
        cv_url=cv_url()
    )
