from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.i18n import JavaScriptCatalog

from .ideax.urls import urlpatterns as ideax_urls

urlpatterns = [
    path('martor/', include('martor.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
    path('admin/', admin.site.urls),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),

    # Apps
    # TODO: namespace
    url('^administration', include(('ideax.administration.urls', 'administration'), namespace='administration')),
    # url('', include(('ideax.ideax.urls', 'ideax'), namespace='ideax')),
    url('', include(('ideax.users.urls', 'users'), namespace='users')),
    url('', include(('ideax.tenant.urls', 'tenant'), namespace='tenant')),
]

urlpatterns += ideax_urls
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
