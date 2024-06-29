from django.urls import path
from .views import (
    ItemListView,
    ListaOrdenesVenta,
    DetalleOrdenVenta,
    ListaItemsOrdenVenta,
    DetalleItemOrdenVenta,
    OrdenVentaCRUDView,
    actualizar_orden_de_compra,
    procesar_orden_venta_excel,
    upload_pdf_cobro,
    ver_cobros_orden_venta,
    ver_ordenes_compra,
    ver_ordenes_pago,
    eliminar_orden_de_compra
)

from . import views

urlpatterns = [
    #restapi
    path("ordenesventa/", ListaOrdenesVenta.as_view(), name="lista_ordenesventa"),
    path("ordenesventa/<int:pk>/", DetalleOrdenVenta.as_view(), name="detalle_ordenventa"),
    path("itemsordenesventa/",ListaItemsOrdenVenta.as_view(),name="lista_itemsordenesventa",),
    path("itemsordenesventa/<int:pk>/",DetalleItemOrdenVenta.as_view(),name="detalle_itemordenventa",
    ),
    
    # A partir de aqui recien las funcionalidades
    path("", OrdenVentaCRUDView.as_view(), name="ordenventa-crud"),
    path("cargar-orden-venta/", procesar_orden_venta_excel, name="cargar_orden_venta"),
    path("ordenventa/procesar/<int:ordenventa_id>/",procesar_orden_venta_excel,name="procesar_orden_venta_excel",),
    
    
    # * nuevo metodo de items y pedidos
    path('items/', ItemListView.as_view(), name='item_list'),
    path('items/<int:ordenventa_id>/', ItemListView.as_view(), name='filtered_item_list'),

    path("ordenes-compra/", ver_ordenes_compra, name="todas_ordenes_compra"),
    path(
        "ordenes-compra/<int:ordenventa_id>/",
        ver_ordenes_compra,
        name="ver_ordenes_compra",
    ),
    path(
        "orden-compra/actualizar/<int:id>/",
        actualizar_orden_de_compra,
        name="actualizar_orden_compra",
    ),
    path("orden-compra/eliminar/<int:id>/", eliminar_orden_de_compra, name="eliminar_orden_compra"),

    # ordenes fake de pago :)
    path(
        "ordenes-pago/<int:ordenventa_id>/",
        views.ver_ordenes_pago,
        name="ver_ordenes_pago",
    ),
    # cobros :P
    path('ver_cobros_orden_venta/<int:ordenventa_id>/', ver_cobros_orden_venta, name='ver_cobros_orden_venta'),
    # cobro automatico:
    path('upload-pdf-cobro/<int:ordenventa_id>/', upload_pdf_cobro, name='upload_pdf_cobro'),
    #ver coborso
    path('ordenventa/<int:ordenventa_id>/facturas/', views.ver_facturas_por_ordenventa, name='ver_facturas_por_ordenventa'),
    path('ordenventa/editar/<int:factura_id>/', views.editar_factura, name='editar_factura'),
    path('ordenventa/factura/eliminar/<int:factura_id>/', views.eliminar_factura, name='eliminar_factura'),

]
