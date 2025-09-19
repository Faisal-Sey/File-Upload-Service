import os

from rest_framework import serializers

from file_upload.models import UploadedFile
from django.conf import settings


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = [
            'id', 'original_filename', 'file_type', 'file_size',
            'storage_backend', 'public_url', 'secure_url',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'storage_backend', 'public_url', 'secure_url',
            'metadata', 'created_at', 'updated_at'
        ]


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    file_type = serializers.ChoiceField(
        choices=['image', 'document', 'video', 'audio', 'other'],
        required=False
    )

    @staticmethod
    def validate_file(value):
        if value.size > settings.MAX_FILE_SIZE:
            raise serializers.ValidationError(
                f"File size must be less than {settings.MAX_FILE_SIZE // (1024 * 1024)}MB"
            )

        file_ext = os.path.splitext(value.name)[1].lower()
        allowed_extensions = (
                settings.ALLOWED_IMAGE_EXTENSIONS +
                settings.ALLOWED_DOCUMENT_EXTENSIONS
        )

        if file_ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"File extension {file_ext} is not allowed"
            )

        return value