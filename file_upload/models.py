import os
import uuid

from django.db import models

from file_upload.utils import get_storage_backend


class UploadedFile(models.Model):
    STORAGE_CHOICES = [
        ('cloudinary', 'Cloudinary'),
        ('s3', 'Amazon S3'),
        ('local', 'Local Storage'),
    ]

    FILE_TYPE_CHOICES = [
        ('image', 'Image'),
        ('document', 'Document'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_id = models.TextField(blank=True)
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default='other')
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    storage_backend = models.CharField(
        max_length=20,
        choices=STORAGE_CHOICES,
        default='cloudinary'
    )

    cloudinary_public_id = models.CharField(max_length=255, null=True, blank=True)
    s3_key = models.CharField(max_length=500, null=True, blank=True)
    local_path = models.CharField(max_length=500, null=True, blank=True)

    public_url = models.URLField(max_length=500)
    secure_url = models.URLField(max_length=500, null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['request_id', '-created_at']),
            models.Index(fields=['file_type']),
            models.Index(fields=['storage_backend']),
        ]

    def __str__(self):
        return f"{self.original_filename} ({self.file_type})"

    def delete_from_storage(self):
        storage = get_storage_backend()
        return storage.delete_file(self)

