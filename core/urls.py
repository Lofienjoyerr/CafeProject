from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path('api/v1/', include('users.urls')),
    path('api/v1/', include('cafe.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.DEBUG:
    urlpatterns = [
                      *urlpatterns,
                  ] + debug_toolbar_urls()
