from xml.etree.ElementTree import Element, SubElement, tostring

from flask import Blueprint, Response, abort, current_app, render_template, flash, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError

from .database import db
from .models.message import Message
from .portfolio_data import portfolio
from .forms import ContactForm
from .models.project import Project
from .models.content import Profile, SiteSettings, Skill, TimelineEntry
from .storage import cv_url

main = Blueprint("main", __name__)

CANONICAL_SITE_URL = "https://binodbajgai.com.np/"


@main.get("/sitemap.xml")
def sitemap():
    """Serve the sitemap for public, indexable portfolio pages."""
    urlset = Element(
        "urlset",
        xmlns="http://www.sitemaps.org/schemas/sitemap/0.9",
    )
    url = SubElement(urlset, "url")
    SubElement(url, "loc").text = CANONICAL_SITE_URL

    xml = tostring(urlset, encoding="utf-8", xml_declaration=True)
    return Response(xml, content_type="application/xml; charset=utf-8")


@main.get("/robots.txt")
def robots():
    return Response(
        "User-agent: *\nAllow: /\nDisallow: /admin/\n\n"
        f"Sitemap: {CANONICAL_SITE_URL}sitemap.xml\n",
        content_type="text/plain; charset=utf-8",
    )


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

    active_portfolio = dict(portfolio)
    active_portfolio["personal"] = Profile.query.first() or portfolio["personal"]
    active_portfolio["skills"] = Skill.query.order_by(Skill.position, Skill.id).all() or portfolio["skills"]
    active_portfolio["experience"] = TimelineEntry.query.order_by(TimelineEntry.position, TimelineEntry.id).all() or portfolio["experience"]

    return render_template(
        "index.html",
        portfolio=active_portfolio,
        form=form,
        projects=projects,
        cv_url=cv_url(),
        site_settings=SiteSettings.query.first(),
    )
