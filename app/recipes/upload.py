import os.path
import secrets
import shutil

from fastapi import UploadFile

UPLOAD_DIR = "upload"


def upload_image(file: UploadFile) -> str:
    file_name = file.filename
    file_path = f"{UPLOAD_DIR}/images/{file_name}"

    if os.path.exists(file_path):
        hash = secrets.token_urlsafe(6)
        file_name = f"{hash}_{file_name}"
        file_path = f"{UPLOAD_DIR}/images/{file_name}"

    with open(file_path, "wb") as dst:
        shutil.copyfileobj(file.file, dst)

    assert file_name
    return file_name
