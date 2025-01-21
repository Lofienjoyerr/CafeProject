from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView

urlpatterns = [
    path('api/v1/', include('users.urls')),
    path('api/v1/', include('cafe.urls')),
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns = [
                      *urlpatterns,
                  ] + debug_toolbar_urls()
