from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from file_upload import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('files/', views.FileListView.as_view(), name='file_list'),
    path('files/<uuid:pk>/', views.FileDetailView.as_view(), name='file_detail'),
    path('files/<uuid:file_id>/url/', views.get_file_url, name='get_file_url'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
