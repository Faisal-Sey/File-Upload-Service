import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from typing import Dict, Any
import uuid
import os

from file_upload.storages.base_storage import BaseStorage


class S3Storage(BaseStorage):
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        self.region = getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')

    def upload_file(self, file, filename: str, file_type: str, **kwargs) -> Dict[str, Any]:
        try:
            file_ext = os.path.splitext(filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            s3_key = f"{file_type}s/{unique_filename}"

            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': self._get_content_type(file_ext),
                    'MetadataDirective': 'REPLACE',
                    'Metadata': {
                        'original-filename': filename,
                        'file-type': file_type,
                        'uploaded-by': str(kwargs.get('request_id', 'anonymous'))
                    }
                }
            )

            public_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"

            return {
                'public_url': public_url,
                'secure_url': public_url,
                'storage_id': s3_key,
                'metadata': {
                    'bucket': self.bucket_name,
                    'region': self.region,
                    's3_key': s3_key,
                }
            }

        except ClientError as e:
            raise Exception(f"S3 upload failed: {str(e)}")

    def delete_file(self, uploaded_file) -> bool:
        try:
            if not uploaded_file.s3_key:
                return False

            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=uploaded_file.s3_key
            )
            return True

        except ClientError as e:
            print(f"S3 delete failed: {str(e)}")
            return False

    def get_file_url(self, uploaded_file, **kwargs) -> str:
        if not uploaded_file.s3_key:
            return uploaded_file.public_url

        try:
            if 'expires_in' in kwargs:
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': uploaded_file.s3_key},
                    ExpiresIn=kwargs['expires_in']
                )
                return url
            else:
                return uploaded_file.public_url

        except ClientError as e:
            print(f"S3 URL generation failed: {str(e)}")
            return uploaded_file.public_url

    @staticmethod
    def _get_content_type(file_ext: str) -> str:
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
        }
        return content_types.get(file_ext.lower(), 'application/octet-stream')