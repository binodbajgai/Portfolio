import os
from io import BytesIO
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
from .forms import (
    AdminLoginForm, ProjectForm, CVUploadForm, ProfileForm, SiteSettingsForm, SkillForm,
    TimelineEntryForm,
)
from .models.content import Profile, SiteSettings, Skill, TimelineEntry
from .models.message import Message
from .models.project import Project
from .storage import StorageError, cv_exists, cv_url, save_blob, save_cv

admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


def _display_order(value):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _save_project_image(image_file, folder="projects"):

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
        output = BytesIO()

        if image_format == "JPEG":
            image = image.convert("RGB")
            image.save(output, format="JPEG", quality=90, optimize=True)
        elif image_format == "PNG":
            image.save(output, format="PNG", optimize=True)
        else:
            image.save(output, format="WEBP", quality=90, method=6)

    image_file.stream.seek(0)

    blob_path = f"images/{folder}/{unique_name}"
    blob_url = save_blob(
        blob_path,
        output.getvalue(),
        f"image/{image_format.lower().replace('jpeg', 'jpg')}"
    )

    if blob_url:
        return blob_url

    upload_dir = Path(current_app.static_folder) / "images" / folder
    os.makedirs(upload_dir, exist_ok=True)
    output_path = upload_dir / unique_name
    output_path.write_bytes(output.getvalue())

    return blob_path


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


@admin.route("/cv", methods=["GET", "POST"])
def cv():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    form = CVUploadForm()
    current_cv = cv_url()

    if form.validate_on_submit():

        try:
            save_cv(form.cv.data)
        except (StorageError, OSError):
            current_app.logger.exception("Failed to save CV file")
            flash("Upload failed. Please try again.", "danger")
        else:
            flash("CV uploaded successfully!", "success")
            return redirect(url_for("admin.cv"))

    try:
        has_cv = cv_exists()
    except StorageError:
        current_app.logger.exception("Failed to check CV file")
        has_cv = False

    return render_template(
        "admin/cv.html",
        form=form,
        current_cv=current_cv,
        cv_exists=has_cv
    )


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

        try:
            image_path = _save_project_image(form.image.data)
        except (StorageError, OSError, ValueError):
            current_app.logger.exception("Failed to save project image")
            flash("Project image upload failed. Please try again.", "danger")
            return render_template(
                "admin/project_form.html",
                form=form,
                title="Add Project",
                project=None,
            )

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
        title="Add Project",
        project=None,
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
            try:
                project.image = _save_project_image(form.image.data)
            except (StorageError, OSError, ValueError):
                current_app.logger.exception("Failed to save project image")
                flash("Project image upload failed. Please try again.", "danger")
                return render_template(
                    "admin/project_form.html",
                    form=form,
                    title="Edit Project",
                    project=project,
                )

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
        title="Edit Project",
        project=project,
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


@admin.route("/profile", methods=["GET", "POST"])
def profile():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    profile_record = Profile.query.first()
    if not profile_record:
        abort(500)

    form = ProfileForm(obj=profile_record)
    if form.validate_on_submit():
        for field in ("name", "title", "description", "location", "email", "phone", "github", "linkedin", "roles"):
            setattr(profile_record, field, getattr(form, field).data)
        if form.photo.data and getattr(form.photo.data, "filename", ""):
            try:
                profile_record.photo = _save_project_image(form.photo.data, "profile")
            except (StorageError, OSError, ValueError):
                current_app.logger.exception("Failed to save profile photo")
                flash("Profile photo upload failed. Please try again.", "danger")
                return render_template("admin/profile_form.html", form=form)
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Failed to update profile")
            abort(500)
        flash("Profile updated successfully!", "success")
        return redirect(url_for("admin.profile"))

    return render_template("admin/profile_form.html", form=form)


@admin.route("/site-copy", methods=["GET", "POST"])
def site_copy():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))
    settings = SiteSettings.query.first()
    if not settings:
        abort(500)
    form = SiteSettingsForm(obj=settings)
    if form.validate_on_submit():
        for field in form._fields:
            if field not in {"csrf_token", "submit"}:
                setattr(settings, field, getattr(form, field).data)
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Failed to update site copy")
            abort(500)
        flash("Site copy updated successfully!", "success")
        return redirect(url_for("admin.site_copy"))
    return render_template("admin/site_settings_form.html", form=form)


@admin.route("/skills")
def skills():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))
    return render_template("admin/skills.html", skills=Skill.query.order_by(Skill.position, Skill.id).all())


@admin.route("/skills/add", methods=["GET", "POST"])
@admin.route("/skills/edit/<int:skill_id>", methods=["GET", "POST"])
def edit_skill(skill_id=None):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))
    skill = Skill.query.get_or_404(skill_id) if skill_id else Skill()
    form = SkillForm(obj=skill)
    if form.validate_on_submit():
        skill.name, skill.icon, skill.description = form.name.data, form.icon.data, form.description.data
        skill.position = _display_order(form.position.data)
        try:
            db.session.add(skill)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Failed to save skill")
            abort(500)
        flash("Skill saved successfully!", "success")
        return redirect(url_for("admin.skills"))
    return render_template("admin/skill_form.html", form=form, title="Edit Skill" if skill_id else "Add Skill")


@admin.route("/skills/delete/<int:skill_id>", methods=["POST"])
def delete_skill(skill_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))
    try:
        db.session.delete(Skill.query.get_or_404(skill_id))
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Failed to delete skill")
        abort(500)
    flash("Skill deleted successfully!", "success")
    return redirect(url_for("admin.skills"))


@admin.route("/timeline")
def timeline():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))
    entries = TimelineEntry.query.order_by(TimelineEntry.position, TimelineEntry.id).all()
    return render_template("admin/timeline.html", entries=entries)


@admin.route("/timeline/add", methods=["GET", "POST"])
@admin.route("/timeline/edit/<int:entry_id>", methods=["GET", "POST"])
def edit_timeline_entry(entry_id=None):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))
    entry = TimelineEntry.query.get_or_404(entry_id) if entry_id else TimelineEntry()
    form = TimelineEntryForm(obj=entry)
    if form.validate_on_submit():
        kind = form.kind.data.strip().lower()
        if kind not in {"experience", "achievement"}:
            form.kind.errors.append("Choose either experience or achievement.")
        else:
            entry.kind, entry.year, entry.title = kind, form.year.data, form.title.data
            entry.organization, entry.description = form.organization.data, form.description.data
            entry.position = _display_order(form.position.data)
            try:
                db.session.add(entry)
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                current_app.logger.exception("Failed to save timeline entry")
                abort(500)
            flash("Timeline entry saved successfully!", "success")
            return redirect(url_for("admin.timeline"))
    return render_template("admin/timeline_form.html", form=form, title="Edit Timeline Entry" if entry_id else "Add Timeline Entry")


@admin.route("/timeline/delete/<int:entry_id>", methods=["POST"])
def delete_timeline_entry(entry_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))
    try:
        db.session.delete(TimelineEntry.query.get_or_404(entry_id))
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Failed to delete timeline entry")
        abort(500)
    flash("Timeline entry deleted successfully!", "success")
    return redirect(url_for("admin.timeline"))







@admin.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("admin.login"))
