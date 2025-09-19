from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseStorage(ABC):
    """Abstract base class for all storage backends"""

    @abstractmethod
    def upload_file(self, file, filename: str, file_type: str, **kwargs) -> Dict[str, Any]:
        """
        Upload a file to the storage backend

        Args:
            file: File object to upload
            filename: Original filename
            file_type: Type of file (image, document, etc.)
            **kwargs: Additional parameters

        Returns:
            Dict containing upload result with keys:
            - public_url: Public URL to access the file
            - secure_url: Secure URL (if available)
            - storage_id: Unique identifier for the file in the storage
            - metadata: Additional metadata
        """
        pass

    @abstractmethod
    def delete_file(self, uploaded_file) -> bool:
        """
        Delete a file from the storage backend

        Args:
            uploaded_file: UploadedFile instance

        Returns:
            bool: True if deletion was successful
        """
        pass

    @abstractmethod
    def get_file_url(self, uploaded_file, **kwargs) -> str:
        """
        Get URL for a file with optional transformations

        Args:
            uploaded_file: UploadedFile instance
            **kwargs: Transformation parameters

        Returns:
            str: URL to access the file
        """
        pass
