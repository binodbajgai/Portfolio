from flask import Blueprint, abort, current_app, render_template, flash, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError

from .database import db
from .models.message import Message
from .portfolio_data import portfolio
from .forms import ContactForm
from .models.project import Project

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

        except SQLAlchemyError:

            db.session.rollback()
            current_app.logger.exception("Failed to save contact message")
            abort(500)

        flash(
            "Your message has been sent successfully!",
            "success"
        )

        return redirect(url_for("main.home"))

    projects = Project.query.order_by(Project.id.desc()).all()

    return render_template(
        "index.html",
        portfolio=portfolio,
        form=form,
        projects=projects
    )
