import os

from django.http import JsonResponse
from django.conf import settings


class FileUploadMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and request.content_type.startswith('multipart/form-data'):
            if hasattr(request, 'FILES') and request.FILES:
                for field_name, uploaded_file in request.FILES.items():
                    if uploaded_file.size > getattr(settings, 'MAX_FILE_SIZE', 10485760):
                        return JsonResponse({
                            'error': f'File {uploaded_file.name} exceeds maximum size limit'
                        }, status=413)

                    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                    allowed_extensions = (
                            getattr(settings, 'ALLOWED_IMAGE_EXTENSIONS', []) +
                            getattr(settings, 'ALLOWED_DOCUMENT_EXTENSIONS', [])
                    )

                    if allowed_extensions and file_ext not in allowed_extensions:
                        return JsonResponse({
                            'error': f'File extension {file_ext} is not allowed'
                        }, status=400)

        response = self.get_response(request)
        return response