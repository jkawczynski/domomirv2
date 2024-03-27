import os.path
import secrets
import shutil

from config import get_settings
from fastapi import UploadFile

settings = get_settings()


def upload_image(file: UploadFile) -> str:
    file_name = file.filename
    assert file_name
    file_path = os.path.join(settings.upload_images_dir, file_name)

    if os.path.exists(file_path):
        hash = secrets.token_urlsafe(6)
        file_name = f"{hash}_{file_name}"
        file_path = os.path.join(settings.upload_images_dir, file_name)

    with open(file_path, "wb") as dst:
        shutil.copyfileobj(file.file, dst)

    assert file_name
    return file_name
