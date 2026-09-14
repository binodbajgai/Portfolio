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

        db.create_all()

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
            "img-src 'self' data:; "
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
