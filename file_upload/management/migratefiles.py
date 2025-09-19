from django.core.management.base import BaseCommand
from django.conf import settings
from file_upload.models import UploadedFile
from file_upload.utils import get_storage_backend


class Command(BaseCommand):
    help = 'Migrate files from one storage backend to another'

    def add_arguments(self, parser):
        parser.add_argument(
            '--from-backend',
            type=str,
            required=True,
            choices=['cloudinary', 's3', 'local'],
            help='Source storage backend'
        )
        parser.add_argument(
            '--to-backend',
            type=str,
            required=True,
            choices=['cloudinary', 's3', 'local'],
            help='Target storage backend'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually doing it'
        )

    def handle(self, *args, **options):
        from_backend = options['from_backend']
        to_backend = options['to_backend']
        dry_run = options['dry_run']

        if from_backend == to_backend:
            self.stdout.write(
                self.style.ERROR('Source and target backends cannot be the same')
            )
            return

        files_to_migrate = UploadedFile.objects.filter(storage_backend=from_backend)

        if not files_to_migrate.exists():
            self.stdout.write(
                self.style.WARNING(f'No files found for backend: {from_backend}')
            )
            return

        self.stdout.write(
            f'Found {files_to_migrate.count()} files to migrate from {from_backend} to {to_backend}'
        )

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No files will be migrated'))
            for file_obj in files_to_migrate:
                self.stdout.write(f'Would migrate: {file_obj.original_filename}')
            return

        original_backend = getattr(settings, 'FILE_UPLOAD_STORAGE_BACKEND', 'cloudinary')
        settings.FILE_UPLOAD_STORAGE_BACKEND = to_backend

        migrated_count = 0
        failed_count = 0

        for file_obj in files_to_migrate:
            try:
                file_content = self._download_file_content(file_obj, from_backend)

                if file_content:
                    new_storage = get_storage_backend()
                    upload_result = new_storage.upload_file(
                        file=file_content,
                        filename=file_obj.original_filename,
                        file_type=file_obj.file_type,
                        request_id=file_obj.request_id
                    )

                    # Update file record
                    file_obj.storage_backend = to_backend
                    file_obj.public_url = upload_result['public_url']
                    file_obj.secure_url = upload_result.get('secure_url')
                    file_obj.metadata.update(upload_result.get('metadata', {}))

                    # Clear old storage-specific fields and set new ones
                    file_obj.cloudinary_public_id = None
                    file_obj.s3_key = None
                    file_obj.local_path = None

                    if to_backend == 'cloudinary':
                        file_obj.cloudinary_public_id = upload_result['storage_id']
                    elif to_backend == 's3':
                        file_obj.s3_key = upload_result['storage_id']
                    elif to_backend == 'local':
                        file_obj.local_path = upload_result['storage_id']

                    file_obj.save()

                    self.stdout.write(
                        self.style.SUCCESS(f'Migrated: {file_obj.original_filename}')
                    )
                    migrated_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to download: {file_obj.original_filename}')
                    )
                    failed_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Migration failed for {file_obj.original_filename}: {str(e)}')
                )
                failed_count += 1

        settings.FILE_UPLOAD_STORAGE_BACKEND = original_backend

        self.stdout.write(
            self.style.SUCCESS(
                f'Migration completed: {migrated_count} succeeded, {failed_count} failed'
            )
        )

    @staticmethod
    def _download_file_content(file_obj, backend):
        import requests
        from io import BytesIO

        try:
            if backend in ['cloudinary', 's3']:
                response = requests.get(file_obj.secure_url or file_obj.public_url)
                if response.status_code == 200:
                    return BytesIO(response.content)
            elif backend == 'local':
                if file_obj.local_path:
                    with open(file_obj.local_path, 'rb') as f:
                        return BytesIO(f.read())
        except Exception as e:
            print(f"Error downloading file: {str(e)}")

        return None