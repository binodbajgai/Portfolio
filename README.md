# Binod Portfolio

A personal portfolio website built with Flask, featuring a public-facing site with project showcase and contact form, plus a password-protected admin dashboard for managing content.

**Live site:** https://binodbajgai.com.np/

---

## Features

- Public portfolio pages (home, projects, about, contact)
- Contact form that stores messages in the database
- Admin dashboard (login-protected) for:
  - Adding, editing, and deleting projects
  - Viewing and deleting contact messages
  - Image uploads for project thumbnails
  - CV uploads stored in Vercel Blob in production
- CSRF protection on all state-changing forms
- Secure session cookies (`HttpOnly`, `Secure`, `SameSite=Lax`)
- Security headers on every response (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy)
- Hashed admin password (no plaintext credentials in code or config)
- Server-side image validation on upload (rejects files that aren't real images regardless of extension)

---

## Tech Stack

| Layer | Tool |
|---|---|
| Backend | Flask 3.x |
| ORM | Flask-SQLAlchemy |
| Forms / CSRF | Flask-WTF |
| Database | PostgreSQL (Render-managed) |
| Image handling | Pillow |
| WSGI server | Gunicorn |
| Hosting | Render |

---


## Environment Variables

The app will not start unless all of these are set. There are no default fallbacks, on purpose.

| Variable | Description |
|---|---|
| `SECRET_KEY` | Flask session signing key. Generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | PostgreSQL connection string, e.g. `postgresql://user:pass@host/dbname?sslmode=require` |
| `ADMIN_USERNAME` | Admin login username |
| `ADMIN_PASSWORD_HASH` | Hashed admin password. Generate with `python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-password'))"` |
| `SESSION_COOKIE_SECURE` | Optional, defaults to `1` (enabled). Set to `0` only for local HTTP development. |
| `BLOB_PUBLIC_URL` | Public base URL of the Vercel Blob store, used for the CV file URL. |
| `BLOB_READ_WRITE_TOKEN` | Vercel Blob read-write token used by the server to replace the CV. |

None of these values should ever be committed to the repository. Locally, keep them in a `.env` file that is listed in `.gitignore`. In production, set them directly in the Render dashboard under the service's **Environment** tab.

For Vercel deployment, create a Blob store in the project and add
`BLOB_PUBLIC_URL` and `BLOB_READ_WRITE_TOKEN` to the project's Environment
Variables. The CV is uploaded to the fixed `Binod_Bajgai_CV.pdf` path, so each
new upload replaces the previous file. Without these variables, local
development continues to use `app/static/files/`.

---

## Local Development

```bash
# clone
git clone https://github.com/bajgaibenod-sketch/portfolio.git
cd binod-portfolio

# create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# install dependencies
pip install -r requirements.txt

# set environment variables (create a .env file, see table above)

# run
python wsgi.py
```

The app creates its database tables automatically on startup via `db.create_all()`, so no manual migration step is needed for a fresh database.

---

## Deployment (Render)

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn wsgi:app`
- **Database:** Render-managed PostgreSQL, connected via the **Internal Database URL** (must be in the same region as the web service)
- Environment variables are set in the Render dashboard, not in code

---

## Security Notes

This project went through a dedicated security hardening pass. Summary of what's in place:

- Secrets are read exclusively from environment variables; the app fails fast on startup if any are missing
- Git history was purged of a previously committed `.env` file
- CSRF tokens are required on all POST forms, including admin delete actions
- Admin password is stored as a salted hash, never in plaintext
- Sessions are cleared and regenerated on login to prevent session fixation
- Uploaded images are validated by content, not just file extension
- Database writes are wrapped in try/except with rollback on failure
- Unhandled exceptions return a generic error page instead of a stack trace

If you find a security issue in this project, please don't open a public GitHub issue — fix it privately first, then document what was changed.

---

## License

Personal project — not currently licensed for reuse.
