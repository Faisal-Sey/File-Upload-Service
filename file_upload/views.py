from datetime import datetime, UTC
import uuid

from rest_framework import status, generics
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.response import Response

from file_upload.models import UploadedFile
from file_upload.serializers.upload import FileUploadSerializer, UploadedFileSerializer
from file_upload.services.file_service import FileUploadService


@api_view(['GET'])
def health_check(request):
    return Response(
        {
            "status": "ok",
            "message": "Service is healthy",
            "timestamp": datetime.now(UTC).isoformat()
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@parser_classes([MultiPartParser, FileUploadParser])
def upload_file(request):
    try:
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            file_type = serializer.validated_data.get('file_type')

            uploaded_file = FileUploadService.upload_file(
                file=file,
                request_id=str(uuid.uuid4()),
                file_type=file_type
            )

            response_serializer = UploadedFileSerializer(uploaded_file)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class FileListView(generics.ListAPIView):
    serializer_class = UploadedFileSerializer

    def get_queryset(self):
        return UploadedFile.objects.all()


class FileDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = UploadedFileSerializer

    def get_queryset(self):
        return UploadedFile.objects.all()

    def perform_destroy(self, instance):
        FileUploadService.delete_file(instance)


@api_view(['GET'])
def get_file_url(request, file_id):
    try:
        uploaded_file = UploadedFile.objects.get(id=file_id)

        # if uploaded_file.user and uploaded_file.user != request.user:
        #     return Response(
        #         {'error': 'Permission denied'},
        #         status=status.HTTP_403_FORBIDDEN
        #     )

        transformations = {}
        if 'width' in request.GET:
            transformations['width'] = int(request.GET['width'])
        if 'height' in request.GET:
            transformations['height'] = int(request.GET['height'])
        if 'quality' in request.GET:
            transformations['quality'] = request.GET['quality']
        if 'format' in request.GET:
            transformations['format'] = request.GET['format']
        if 'expires_in' in request.GET:
            transformations['expires_in'] = int(request.GET['expires_in'])

        url = FileUploadService.get_file_url(uploaded_file, **transformations)

        return Response({'url': url})

    except UploadedFile.DoesNotExist:
        return Response(
            {'error': 'File not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )