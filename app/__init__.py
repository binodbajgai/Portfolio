from flask import Flask

from .admin import admin
from .database import db


def create_app():

    app = Flask(__name__)

    app.config.from_object("config.Config")

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)
    app.register_blueprint(admin)

    with app.app_context():
        from .models.message import Message
        db.create_all()

    return app