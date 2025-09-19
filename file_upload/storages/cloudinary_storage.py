import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Dict, Any
import os

from file_upload.storages.base_storage import BaseStorage


class CloudinaryStorage(BaseStorage):
    def upload_file(self, file, filename: str, file_type: str, **kwargs) -> Dict[str, Any]:
        try:
            name_without_ext = os.path.splitext(filename)[0]
            public_id = f"{file_type}s/{name_without_ext}_{kwargs.get('request_id', 'anonymous')}"

            upload_params = {
                'public_id': public_id,
                'resource_type': 'auto',
                'unique_filename': True,
                'overwrite': False,
            }

            if file_type == 'image':
                upload_params.update({
                    'transformation': [
                        {'quality': 'auto:good'},
                        {'fetch_format': 'auto'}
                    ]
                })

            result = cloudinary.uploader.upload(file, **upload_params)

            return {
                'public_url': result['secure_url'],
                'secure_url': result['secure_url'],
                'storage_id': result['public_id'],
                'metadata': {
                    'cloudinary_version': result.get('version'),
                    'width': result.get('width'),
                    'height': result.get('height'),
                    'format': result.get('format'),
                    'resource_type': result.get('resource_type'),
                    'bytes': result.get('bytes'),
                }
            }

        except Exception as e:
            raise Exception(f"Cloudinary upload failed: {str(e)}")

    def delete_file(self, uploaded_file) -> bool:
        try:
            if not uploaded_file.cloudinary_public_id:
                return False

            result = cloudinary.uploader.destroy(
                uploaded_file.cloudinary_public_id,
                resource_type='auto'
            )
            return result.get('result') == 'ok'

        except Exception as e:
            print(f"Cloudinary delete failed: {str(e)}")
            return False

    def get_file_url(self, uploaded_file, **kwargs) -> str:
        if not uploaded_file.cloudinary_public_id:
            return uploaded_file.public_url

        try:
            transformations = []

            if uploaded_file.file_type == 'image':
                if 'width' in kwargs or 'height' in kwargs:
                    transform = {}
                    if 'width' in kwargs:
                        transform['width'] = kwargs['width']
                    if 'height' in kwargs:
                        transform['height'] = kwargs['height']
                    transform['crop'] = kwargs.get('crop', 'fill')
                    transformations.append(transform)

                if 'quality' in kwargs:
                    transformations.append({'quality': kwargs['quality']})

                if 'format' in kwargs:
                    transformations.append({'fetch_format': kwargs['format']})

            if transformations:
                url, _ = cloudinary.utils.cloudinary_url(
                    uploaded_file.cloudinary_public_id,
                    transformation=transformations,
                    secure=True
                )
                return url
            else:
                return uploaded_file.secure_url or uploaded_file.public_url

        except Exception as e:
            print(f"Cloudinary URL generation failed: {str(e)}")
            return uploaded_file.public_url