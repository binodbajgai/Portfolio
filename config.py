import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


def _bool_env(name, default=False):

    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() not in {"0", "false", "no", "off"}


def _required_env(name):

    value = os.getenv(name)

    if not value:

        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )

    return value


def _session_lifetime():

    value = os.getenv("SESSION_LIFETIME_DAYS", "30").strip()

    try:
        days = int(value)
    except ValueError as error:
        raise RuntimeError(
            "SESSION_LIFETIME_DAYS must be a positive whole number"
        ) from error

    if days <= 0:
        raise RuntimeError(
            "SESSION_LIFETIME_DAYS must be a positive whole number"
        )

    return timedelta(days=days)


def _database_uri():

    value = _required_env("DATABASE_URL")

    if value.startswith("postgres://"):

        value = value.replace("postgres://", "postgresql://", 1)

    if not value.startswith("postgresql://"):

        raise RuntimeError(
            "DATABASE_URL must be a PostgreSQL connection string"
        )

    if "sslmode=" not in value:

        separator = "&" if "?" in value else "?"
        value = f"{value}{separator}sslmode=require"

    return value


class Config:

    SECRET_KEY = _required_env("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = _database_uri()

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ADMIN_USERNAME = _required_env("ADMIN_USERNAME")
    ADMIN_PASSWORD_HASH = _required_env("ADMIN_PASSWORD_HASH")

    SESSION_COOKIE_SECURE = _bool_env("SESSION_COOKIE_SECURE", default=True)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = _session_lifetime()
