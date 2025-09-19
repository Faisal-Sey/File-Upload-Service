"""
## API Endpoints

### 1. Upload File
POST /api/files/upload/
Content-Type: multipart/form-data

Parameters:
- file: File to upload (required)
- file_type: Type of file - image, document, video, audio, other (optional)

Response:
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "original_filename": "example.jpg",
    "file_type": "image",
    "file_size": 1024000,
    "storage_backend": "cloudinary",
    "public_url": "https://res.cloudinary.com/demo/image/upload/v1/example.jpg",
    "secure_url": "https://res.cloudinary.com/demo/image/upload/v1/example.jpg",
    "metadata": {
        "width": 1920,
        "height": 1080,
        "format": "jpg"
    },
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
}

### 2. List Files
GET /api/files/files/

Response:
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [...]
}

### 3. Get File Details
GET /api/files/files/{file_id}/

### 4. Delete File
DELETE /api/files/files/{file_id}/

### 5. Get File URL with Transformations
GET /api/files/files/{file_id}/url/?width=300&height=300&quality=auto

Parameters (for images):
- width: Desired width
- height: Desired height  
- quality: Image quality (auto, best, good, eco)
- format: Output format (jpg, png, webp, auto)
- crop: Crop mode (fill, fit, scale, etc.)
- expires_in: URL expiration in seconds (for S3)

Response:
{
    "url": "https://res.cloudinary.com/demo/image/upload/w_300,h_300,q_auto/example.jpg"
}

## Python Usage Examples

### Basic Upload
```python
from file_upload.services import FileUploadService
from django.contrib.auth.models import User

user = User.objects.get(username='example')

# Upload file
with open('example.jpg', 'rb') as f:
    uploaded_file = FileUploadService.upload_file(
        file=f,
        user=user,
        file_type='image'
    )

print(f"File uploaded: {uploaded_file.public_url}")
```

### Get Transformed URL
```python
# Get resized image URL
resized_url = FileUploadService.get_file_url(
    uploaded_file,
    width=300,
    height=300,
    quality='auto'
)
```

### Delete File
```python
# Delete file from storage and database
success = FileUploadService.delete_file(uploaded_file)
```

## Frontend Integration Examples

### JavaScript/Fetch
```javascript
const uploadFile = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', 'image');

    const response = await fetch('/api/files/upload/', {
        method: 'POST',
        body: formData,
        headers: {
            'Authorization': 'Bearer ' + token,  // if using token auth
        }
    });

    if (response.ok) {
        const result = await response.json();
        console.log('File uploaded:', result.public_url);
        return result;
    } else {
        throw new Error('Upload failed');
    }
};

// Usage
document.getElementById('file-input').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        try {
            const uploadedFile = await uploadFile(file);
            // Display the uploaded file
            document.getElementById('image-preview').src = uploadedFile.public_url;
        } catch (error) {
            console.error('Upload error:', error);
        }
    }
});
```

### React Component
```jsx
import React, { useState } from 'react';

const FileUploader = () => {
    const [uploading, setUploading] = useState(false);
    const [uploadedFile, setUploadedFile] = useState(null);

    const handleFileUpload = async (file) => {
        setUploading(true);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/files/upload/', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                setUploadedFile(result);
            } else {
                console.error('Upload failed');
            }
        } catch (error) {
            console.error('Upload error:', error);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div>
            <input
                type="file"
                onChange={(e) => {
                    const file = e.target.files[0];
                    if (file) handleFileUpload(file);
                }}
                disabled={uploading}
            />
            {uploading && <p>Uploading...</p>}
            {uploadedFile && (
                <div>
                    <p>File uploaded successfully!</p>
                    <img 
                        src={uploadedFile.public_url} 
                        alt={uploadedFile.original_filename}
                        style={{ maxWidth: '300px' }}
                    />
                </div>
            )}
        </div>
    );
};
```

## Configuration Examples

### Switch to AWS S3
```python
# In settings.py
FILE_UPLOAD_STORAGE_BACKEND = 's3'

# In .env
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-west-2
```

### Add Custom Storage Backend
```python
# Create file_upload/storage/custom_storage.py
from .base import BaseStorage

class CustomStorage(BaseStorage):
    def upload_file(self, file, filename, file_type, **kwargs):
        # Your custom upload logic
        pass

    def delete_file(self, uploaded_file):
        # Your custom delete logic
        pass

    def get_file_url(self, uploaded_file, **kwargs):
        # Your custom URL generation logic
        pass

# Update file_upload/storage/__init__.py
def get_storage_backend():
    backend = getattr(settings, 'FILE_UPLOAD_STORAGE_BACKEND', 'cloudinary')

    if backend == 'custom':
        return CustomStorage()
    # ... existing backends
```

## Management Commands

### Migrate Storage Backend
```bash
# Dry run to see what would be migrated
python manage.py migrate_storage --from-backend=local --to-backend=cloudinary --dry-run

# Actual migration
python manage.py migrate_storage --from-backend=local --to-backend=cloudinary
```

## Installation & Setup

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Add to INSTALLED_APPS in settings.py:
```python
INSTALLED_APPS = [
    # ...
    'file_upload',
]
```

3. Run migrations:
```bash
python manage.py makemigrations file_upload
python manage.py migrate
```

4. Configure environment variables in .env file

5. Add URLs to main urls.py:
```python
urlpatterns = [
    # ...
    path('api/files/', include('file_upload.urls')),
]
```

6. Configure storage backend in settings.py or environment variables

This service provides a robust, extensible file upload solution that can easily switch between different storage providers while maintaining a consistent API.
"""