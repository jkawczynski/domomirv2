from config import get_settings

settings = get_settings()


def _get_base_image_url() -> str:
    return (
        settings.local_images_url
        if settings.serve_local_images
        else settings.imagor_url
    )


def get_image_url(file_name: str) -> str:
    base_url = _get_base_image_url()
    return f"{base_url}/{file_name}"


def get_image_thumbnail_url(file_name: str) -> str:
    if settings.serve_local_images:
        return get_image_url(file_name)

    base_url = _get_base_image_url()
    imagor_filter = "filters:proportion(25):quality(50)"

    return f"{base_url}/{imagor_filter}/{file_name}"


template_filters = {
    "image_url": get_image_url,
    "image_thumbnail": get_image_thumbnail_url,
}
