from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFProtect

from .admin import admin
from .database import db

csrf = CSRFProtect()


def create_app():

    app = Flask(__name__)

    app.config.from_object("config.Config")
    csrf.init_app(app)

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)
    app.register_blueprint(admin)

    with app.app_context():

        from .models.message import Message
        from .models.project import Project
        from .models.content import Profile, SiteSettings, Skill, TimelineEntry
        from .portfolio_data import portfolio

        db.create_all()

        # Seed the content editor once so the existing hard-coded portfolio is
        # immediately editable. Existing editor data is never overwritten.
        if not Profile.query.first():
            profile_data = dict(portfolio["personal"])
            profile_data["roles"] = ", ".join(profile_data["roles"])
            profile_data.pop("cv", None)
            profile_data["photo"] = "images/binod.jpeg"
            db.session.add(Profile(**profile_data))
        if not SiteSettings.query.first():
            db.session.add(SiteSettings(
                hero_greeting="👋 Hello, I'm", projects_stat="5+", technologies_stat="8+",
                journey_stat="2025", projects_heading="Featured Projects",
                projects_description="Here are some of the projects I've built using Python, Flask, AI, and modern web technologies.",
                about_achievement="Runner-up | Hult Prize Softwarica",
                about_projects="AI & Web | Development", skills_heading="Technologies I Work With",
                skills_description="Building intelligent software using modern technologies, clean architecture, and AI-focused development.",
                experience_heading="Experience & Education",
                experience_description="My learning journey, achievements, and projects that have shaped my growth as a software developer.",
                contact_heading="Let's Build Something Amazing",
                contact_description="Have a project, collaboration, or opportunity in mind? I'd love to hear from you.",
            ))
        if not Skill.query.first():
            for position, item in enumerate(portfolio["skills"]):
                db.session.add(Skill(position=position, **item))
        if not TimelineEntry.query.first():
            for position, item in enumerate(portfolio["experience"]):
                db.session.add(TimelineEntry(
                    kind="achievement" if item["title"] == "Runner-up" else "experience",
                    year=item["year"], title=item["title"], organization=item["company"],
                    description=item["description"], position=position,
                ))
        db.session.commit()

    @app.after_request
    def apply_security_headers(response):

        # A form's CSRF token is tied to the user's session. Never cache
        # dynamic responses, otherwise a stale login form can lose that
        # matching session cookie when submitted.
        if not request.path.startswith("/static/"):
            response.cache_control.no_store = True
            response.cache_control.private = True
            response.headers["Pragma"] = "no-cache"

        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = (
            "strict-origin-when-cross-origin"
        )
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "base-uri 'self'; "
            "frame-ancestors 'none'; "
            "img-src 'self' data: https://*.public.blob.vercel-storage.com; "
            "script-src 'self' https://cdnjs.cloudflare.com https://unpkg.com 'unsafe-inline'; "
            "style-src 'self' https://fonts.googleapis.com https://cdnjs.cloudflare.com https://unpkg.com 'unsafe-inline'; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "connect-src 'self'"
        )
        return response

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template("errors/500.html"), 500

    return app
