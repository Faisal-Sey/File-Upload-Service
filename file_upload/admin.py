from django.contrib import admin

from file_upload.models import UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = [
        'original_filename', 'file_type', 'file_size_mb',
        'storage_backend', 'request_id', 'created_at'
    ]
    list_filter = ['file_type', 'storage_backend', 'created_at']
    search_fields = ['original_filename']
    readonly_fields = [
        'id', 'file_size', 'cloudinary_public_id', 's3_key',
        'local_path', 'public_url', 'secure_url', 'metadata',
        'created_at', 'updated_at'
    ]

    def file_size_mb(self, obj):
        return f"{obj.file_size / (1024 * 1024):.2f} MB"

    file_size_mb.short_description = "File Size"
