from config import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from common.swaggers import schema_view


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('account/', include('account.urls', namespace='account')),
    path('core/', include('core.urls')),
    path('search/', include('search.urls')),
    path('timeline/', include('timeline.urls')),
    path('chat/', include('chat.urls')),
    path('activity/', include('activity.urls')),
    path('notification/', include('notification.urls')),
    # swagger urls
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    media_urls = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += media_urls
    # urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))