from flask import Blueprint, render_template, flash, redirect, url_for

from .database import db
from .models.message import Message
from .portfolio_data import portfolio
from .forms import ContactForm

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

        db.session.add(new_message)
        db.session.commit()

        flash(
            "Your message has been sent successfully!",
            "success"
        )

        return redirect(url_for("main.home"))

    return render_template(
        "index.html",
        portfolio=portfolio,
        form=form
    )