import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from flask import current_app
from vercel.blob import BlobClient, BlobError


CV_FILENAME = "Binod_Bajgai_CV.pdf"


class StorageError(RuntimeError):
    """Raised when a CV cannot be read from or written to storage."""


def _blob_cv_url():
    base_url = os.getenv("BLOB_PUBLIC_URL", "").rstrip("/")

    if not base_url:
        return None

    return f"{base_url}/{quote(CV_FILENAME)}"


def cv_url():
    blob_url = _blob_cv_url()

    if blob_url:
        return blob_url

    return current_app.url_for(
        "static",
        filename=f"files/{CV_FILENAME}"
    )


def cv_exists():
    blob_url = _blob_cv_url()

    if not blob_url:
        return (
            Path(current_app.static_folder) / "files" / CV_FILENAME
        ).exists()

    request = Request(blob_url, method="HEAD")

    try:
        with urlopen(request, timeout=10) as response:
            return 200 <= response.status < 400
    except HTTPError as error:
        if error.code == 404:
            return False
        raise StorageError("Could not check the CV in Vercel Blob.") from error
    except URLError as error:
        raise StorageError("Could not reach Vercel Blob.") from error


def save_cv(cv_file):
    if not cv_file or not getattr(cv_file, "filename", ""):
        return None

    token = os.getenv("BLOB_READ_WRITE_TOKEN")
    blob_url = _blob_cv_url()

    if blob_url and token:
        cv_file.stream.seek(0)

        try:
            BlobClient(token=token).put(
                CV_FILENAME,
                cv_file.stream.read(),
                access="public",
                content_type="application/pdf",
                add_random_suffix=False,
                overwrite=True,
            )
        except BlobError as error:
            raise StorageError("Vercel Blob rejected the upload.") from error
        finally:
            cv_file.stream.seek(0)

        return blob_url

    if blob_url or token:
        raise StorageError(
            "Set both BLOB_PUBLIC_URL and BLOB_READ_WRITE_TOKEN "
            "to enable Vercel Blob storage."
        )

    if os.getenv("VERCEL"):
        raise StorageError(
            "Vercel Blob storage is not configured. Set "
            "BLOB_PUBLIC_URL and BLOB_READ_WRITE_TOKEN."
        )

    upload_dir = Path(current_app.static_folder) / "files"
    upload_dir.mkdir(parents=True, exist_ok=True)
    save_path = upload_dir / CV_FILENAME

    cv_file.stream.seek(0)
    with save_path.open("wb") as destination:
        destination.write(cv_file.stream.read())
    cv_file.stream.seek(0)

    return cv_url()
