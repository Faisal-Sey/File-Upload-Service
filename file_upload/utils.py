from io import BytesIO
from typing import Optional, Tuple

from django.conf import settings
from PIL import Image

from file_upload.storages.cloudinary_storage import CloudinaryStorage
from file_upload.storages.local_storage import LocalStorage
from file_upload.storages.s3_storage import S3Storage


def get_storage_backend():
    backend = getattr(settings, 'FILE_UPLOAD_STORAGE_BACKEND', 'cloudinary')

    if backend == 'cloudinary':
        return CloudinaryStorage()
    elif backend == 's3':
        return S3Storage()
    elif backend == 'local':
        return LocalStorage()
    else:
        raise ValueError(f"Unsupported storage backend: {backend}")


def validate_image(file) -> bool:
    """Validate if file is a valid image"""
    try:
        with Image.open(file) as img:
            img.verify()
        file.seek(0)
        return True
    except Exception:
        return False

def get_image_dimensions(file) -> Optional[Tuple[int, int]]:
    """Get image dimensions without loading the full image"""
    try:
        with Image.open(file) as img:
            dimensions = img.size
        file.seek(0)  # Reset file pointer
        return dimensions
    except Exception:
        return None


def resize_image(
        file,
        max_width: int = 1920,
        max_height: int = 1080,
        quality: int = 85
) -> BytesIO:
    try:
        with Image.open(file) as img:
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)

            return output
    except Exception as e:
        print(f"Error resizing image: {str(e)}")
        file.seek(0)
        return file


def generate_thumbnail(file, size: Tuple[int, int] = (300, 300)) -> Optional[BytesIO]:
    try:
        with Image.open(file) as img:
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            img.thumbnail(size, Image.Resampling.LANCZOS)

            output = BytesIO()
            img.save(output, format='JPEG', quality=80, optimize=True)
            output.seek(0)

            return output
    except Exception as e:
        print(f"Error generating thumbnail: {str(e)}")
        return None
