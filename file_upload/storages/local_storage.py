import os
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from typing import Dict, Any

from file_upload.storages.base_storage import BaseStorage


class LocalStorage(BaseStorage):
    """Local file system storage backend implementation"""

    def __init__(self):
        self.media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media'))
        self.media_url = getattr(settings, 'MEDIA_URL', '/media/')

    def upload_file(self, file, filename: str, file_type: str, **kwargs) -> Dict[str, Any]:
        """Upload file to local storage"""
        try:
            # Generate unique filename
            file_ext = os.path.splitext(filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            relative_path = f"{file_type}s/{unique_filename}"

            # Save file
            saved_path = default_storage.save(relative_path, file)
            full_path = os.path.join(self.media_root, saved_path)

            # Generate URL
            public_url = f"{self.media_url}{saved_path}"

            return {
                'public_url': public_url,
                'secure_url': public_url,
                'storage_id': saved_path,
                'metadata': {
                    'full_path': full_path,
                    'relative_path': saved_path,
                }
            }

        except Exception as e:
            raise Exception(f"Local storage upload failed: {str(e)}")

    def delete_file(self, uploaded_file) -> bool:
        """Delete file from local storage"""
        try:
            if not uploaded_file.local_path:
                return False

            if default_storage.exists(uploaded_file.local_path):
                default_storage.delete(uploaded_file.local_path)
                return True
            return False

        except Exception as e:
            print(f"Local storage delete failed: {str(e)}")
            return False

    def get_file_url(self, uploaded_file, **kwargs) -> str:
        """Get local file URL"""
        return uploaded_file.public_url