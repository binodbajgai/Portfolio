from .models.message import Message
from .database import db
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    session,
    current_app
)

from .forms import AdminLoginForm

admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


@admin.route("/login", methods=["GET", "POST"])
def login():

    form = AdminLoginForm()

    if form.validate_on_submit():

        if (
            form.username.data == current_app.config["ADMIN_USERNAME"]
            and
            form.password.data == current_app.config["ADMIN_PASSWORD"]
        ):

            session["admin_logged_in"] = True

            return redirect(url_for("admin.dashboard"))

        flash("Invalid username or password", "danger")

    return render_template(
        "admin/login.html",
        form=form
    )


@admin.route("/")
def dashboard():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    messages = Message.query.order_by(
        Message.created_at.desc()
    ).all()

    return render_template(
        "admin/dashboard.html",
        messages=messages
    )

@admin.route("/message/<int:message_id>")
def view_message(message_id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    message = Message.query.get_or_404(message_id)

    return render_template(
        "admin/view_message.html",
        message=message
    )

@admin.route("/delete/<int:message_id>", methods=["POST"])
def delete_message(message_id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    message = Message.query.get_or_404(message_id)

    db.session.delete(message)
    db.session.commit()

    return redirect(url_for("admin.dashboard"))



@admin.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("admin.login"))