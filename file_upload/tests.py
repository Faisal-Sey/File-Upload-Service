import tempfile
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from .models import UploadedFile
from .services.file_service import FileUploadService


class FileUploadServiceTest(TestCase):
    def setUp(self):
        self.request_id = 'test_request_id'

        # Create a test image file
        self.test_file = SimpleUploadedFile(
            "test_image.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )

    @patch('file_upload.storage.cloudinary_storage.cloudinary')
    def test_upload_file_success(self, mock_cloudinary):
        """Test successful file upload"""
        # Mock Cloudinary response
        mock_cloudinary.uploader.upload.return_value = {
            'public_id': 'test_public_id',
            'secure_url': 'https://res.cloudinary.com/test/image/upload/test.jpg',
            'version': '123456',
            'width': 800,
            'height': 600,
            'format': 'jpg',
            'resource_type': 'image',
            'bytes': 12345
        }

        # Upload file
        uploaded_file = FileUploadService.upload_file(
            file=self.test_file,
            request_id=self.request_id,
            file_type='image'
        )

        # Assertions
        self.assertIsInstance(uploaded_file, UploadedFile)
        self.assertEqual(uploaded_file.request_id, self.request_id)
        self.assertEqual(uploaded_file.original_filename, 'test_image.jpg')
        self.assertEqual(uploaded_file.file_type, 'image')
        self.assertIsNotNone(uploaded_file.cloudinary_public_id)

        # Verify Cloudinary was called
        mock_cloudinary.uploader.upload.assert_called_once()

    def test_file_type_detection(self):
        """Test automatic file type detection"""
        test_cases = [
            ('image.jpg', 'image'),
            ('document.pdf', 'document'),
            ('video.mp4', 'video'),
            ('audio.mp3', 'audio'),
            ('unknown.xyz', 'other'),
        ]

        for filename, expected_type in test_cases:
            detected_type = FileUploadService._detect_file_type(filename)
            self.assertEqual(detected_type, expected_type)

    @override_settings(FILE_UPLOAD_STORAGE_BACKEND='local')
    def test_local_storage_upload(self):
        """Test upload using local storage backend"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(MEDIA_ROOT=temp_dir):
                uploaded_file = FileUploadService.upload_file(
                    file=self.test_file,
                    request_id=self.request_id,
                    file_type='image'
                )

                self.assertEqual(uploaded_file.storage_backend, 'local')
                self.assertIsNotNone(uploaded_file.local_path)
                self.assertTrue(uploaded_file.public_url.startswith('/media/'))
