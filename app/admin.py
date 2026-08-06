import os
from pathlib import Path
from uuid import uuid4

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    session,
    url_for
)
from PIL import Image
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError

from .database import db
from .forms import AdminLoginForm, ProjectForm
from .models.message import Message
from .models.project import Project

admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


def _save_project_image(image_file):

    if not image_file or not getattr(image_file, "filename", ""):
        return None

    filename = secure_filename(image_file.filename)
    stem = Path(filename).stem

    image_file.stream.seek(0)

    with Image.open(image_file.stream) as image:

        image_format = (image.format or "").upper()

        if image_format not in {"JPEG", "PNG", "WEBP"}:
            raise ValueError("Unsupported image format")

        unique_name = f"{stem}_{uuid4().hex[:8]}.{image_format.lower().replace('jpeg', 'jpg')}"
        upload_dir = Path(current_app.static_folder) / "images" / "projects"
        os.makedirs(upload_dir, exist_ok=True)
        save_path = upload_dir / unique_name

        if image_format == "JPEG":
            image = image.convert("RGB")
            image.save(save_path, format="JPEG", quality=90, optimize=True)
        elif image_format == "PNG":
            image.save(save_path, format="PNG", optimize=True)
        else:
            image.save(save_path, format="WEBP", quality=90, method=6)

    image_file.stream.seek(0)

    return f"images/projects/{unique_name}"


@admin.route("/login", methods=["GET", "POST"])
def login():

    form = AdminLoginForm()

    if form.validate_on_submit():

        session.clear()

        if (
            form.username.data == current_app.config["ADMIN_USERNAME"]
            and
            check_password_hash(
                current_app.config["ADMIN_PASSWORD_HASH"],
                form.password.data
            )
        ):

            session["admin_logged_in"] = True
            session.permanent = True

            return redirect(url_for("admin.dashboard"))

        current_app.logger.warning(
            "Invalid admin login attempt for %s",
            form.username.data
        )

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

    try:

        db.session.delete(message)
        db.session.commit()

    except SQLAlchemyError:

        db.session.rollback()
        current_app.logger.exception("Failed to delete message")
        abort(500)

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

        image_path = _save_project_image(form.image.data)

        project = Project(
            title=form.title.data,
            subtitle=form.subtitle.data,
            description=form.description.data,
            image=image_path,
            github=form.github.data,
            demo=form.demo.data,
            tech=form.tech.data
        )

        try:

            db.session.add(project)
            db.session.commit()

        except SQLAlchemyError:

            db.session.rollback()
            current_app.logger.exception("Failed to add project")
            abort(500)

        flash(
            "Project added successfully!",
            "success"
        )

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

        project.title = form.title.data
        project.subtitle = form.subtitle.data
        project.description = form.description.data
        project.github = form.github.data
        project.demo = form.demo.data
        project.tech = form.tech.data

        if form.image.data and getattr(form.image.data, "filename", ""):
            project.image = _save_project_image(form.image.data)

        try:

            db.session.commit()

        except SQLAlchemyError:

            db.session.rollback()
            current_app.logger.exception("Failed to update project")
            abort(500)

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

    try:

        db.session.delete(project)
        db.session.commit()

    except SQLAlchemyError:

        db.session.rollback()
        current_app.logger.exception("Failed to delete project")
        abort(500)

    flash(
        "Project deleted successfully!",
        "success"
    )

    return redirect(url_for("admin.projects"))







@admin.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("admin.login"))
