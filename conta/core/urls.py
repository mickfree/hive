from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("",include('home.urls')),
    path("cronogramas/", include('cronogramas.urls')),
    path("extractos",include('extractos.urls')),
    path("inventario/", include('inventario.urls')), # Incluye las URLs de ordencompra
    path("ordencompra/", include('ordencompra.urls')),
    path("ordenventa/", include('ordenventa.urls')), # Incluye las URLs de ordenventa
    path("reportes/", include('reportes.urls')),
    path("extractos/",include('extractos.urls')),
    path("conciliacion/",include('conciliacion.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)