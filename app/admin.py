from .models.message import Message
from .models.project import Project
from .forms import ProjectForm
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


@admin.route("/projects")
def projects():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    projects = Project.query.order_by(Project.id.desc()).all()

    return render_template(
        "admin/projects.html",
        projects=projects
    )

@admin.route("/projects/add", methods=["GET", "POST"])
def add_project():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    form = ProjectForm()

    if form.validate_on_submit():

        project = Project(

            title=form.title.data,
            subtitle=form.subtitle.data,
            description=form.description.data,
            image=form.image.data,
            github=form.github.data,
            demo=form.demo.data,
            tech=form.tech.data

        )

        db.session.add(project)
        db.session.commit()



        return redirect(url_for("admin.projects"))

    return render_template(
        "admin/project_form.html",
        form=form,
        title="Add Project"
    )

@admin.route("/projects/edit/<int:project_id>", methods=["GET", "POST"])
def edit_project(project_id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    project = Project.query.get_or_404(project_id)

    form = ProjectForm(obj=project)

    if form.validate_on_submit():

        form.populate_obj(project)

        db.session.commit()

        flash(
            "Project updated successfully!",
            "success"
        )

        return redirect(url_for("admin.projects"))

    return render_template(
        "admin/project_form.html",
        form=form,
        title="Edit Project"
    )

@admin.route("/projects/delete/<int:project_id>", methods=["POST"])
def delete_project(project_id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    project = Project.query.get_or_404(project_id)

    db.session.delete(project)
    db.session.commit()

    flash(
        "Project deleted successfully!",
        "success"
    )

    return redirect(url_for("admin.projects"))







@admin.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("admin.login"))