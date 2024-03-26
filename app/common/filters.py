from config import get_settings

settings = get_settings()


def get_image_url(file_name: str) -> str:
    base_url = settings.local_images_url if settings.serve_local_images else "TODO"

    return f"{base_url}/{file_name}"


template_filters = {"image_url": get_image_url}
