from django.urls import path
from reportes import views

urlpatterns = [
    path("", views.reportes_registros, name="ruta_reportes"),
    # Otras URLS de tu aplicación de reportes, si las tienes...
    # REPORTES
    path(
        "reportes/", views.ReportesVentaListView.as_view(), name="reportas-venta-lista"
    ),
    # proveedores:
    path("proveedores/", views.ProveedorListView.as_view(), name="proveedor_list"),
    path(
        "proveedores/nuevo/",
        views.ProveedorCreateView.as_view(),
        name="proveedor_create",
    ),
    path(
        "proveedores/editar/<int:pk>/",
        views.ProveedorUpdateView.as_view(),
        name="proveedor_update",
    ),
    path(
        "proveedores/eliminar/<int:pk>/",
        views.ProveedorDeleteView.as_view(),
        name="proveedor_delete",
    ),
]
