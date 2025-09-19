import os
from typing import Optional

from file_upload.models import UploadedFile
from file_upload.utils import get_storage_backend


class FileUploadService:

    @staticmethod
    def upload_file(
            file,
            request_id: Optional[str] = None,
            file_type: Optional[str] = None
    ) -> UploadedFile:
        """
        Upload a file using the configured storage backend

        Args:
            file: File object to upload
            request_id: Request ID
            file_type: Type of file (will be auto-detected if not provided)

        Returns:
            UploadedFile: The created file record
        """
        if not file_type:
            file_type = FileUploadService._detect_file_type(file.name)

        storage = get_storage_backend()

        upload_result = storage.upload_file(
            file=file,
            filename=file.name,
            file_type=file_type,
            request_id=request_id if request_id else None
        )

        uploaded_file = UploadedFile.objects.create(
            request_id=request_id,
            original_filename=file.name,
            file_type=file_type,
            file_size=file.size,
            storage_backend=storage.__class__.__name__.lower().replace('storage', ''),
            public_url=upload_result['public_url'],
            secure_url=upload_result.get('secure_url'),
            metadata=upload_result.get('metadata', {}),
        )

        if 'cloudinary' in storage.__class__.__name__.lower():
            uploaded_file.cloudinary_public_id = upload_result['storage_id']
        elif 's3' in storage.__class__.__name__.lower():
            uploaded_file.s3_key = upload_result['storage_id']
        elif 'local' in storage.__class__.__name__.lower():
            uploaded_file.local_path = upload_result['storage_id']

        uploaded_file.save()
        return uploaded_file

    @staticmethod
    def delete_file(uploaded_file: UploadedFile) -> bool:
        try:
            success = uploaded_file.delete_from_storage()

            uploaded_file.delete()

            return success
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False

    @staticmethod
    def get_file_url(uploaded_file: UploadedFile, **kwargs) -> str:
        storage = get_storage_backend()
        return storage.get_file_url(uploaded_file, **kwargs)

    @staticmethod
    def _detect_file_type(filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()

        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']
        document_extensions = ['.pdf', '.doc', '.docx', '.txt', '.csv', '.xls', '.xlsx']
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv']
        audio_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg']

        if ext in image_extensions:
            return 'image'
        elif ext in document_extensions:
            return 'document'
        elif ext in video_extensions:
            return 'video'
        elif ext in audio_extensions:
            return 'audio'
        else:
            return 'other'