from django.urls import path

from ordenventa.views import ver_ordenes_pago
from .views import (
    cronograma_ordenes_compra,
    lista_ordenes_venta,
    detalle_orden_compra,
    lista_ordenes_compra2,
    ordenpago,
    ver_detalles_pago,
    actualizar_pago
)

urlpatterns = [
    path("listascreo", lista_ordenes_compra2, name="lista_ordenes_compra"),
    path("ordenpago/", ordenpago, name="ordenpago"),
    path("", lista_ordenes_venta, name="lista_ordenes_venta"),
    path(
        "orden_compra/<int:pk>/ordenes_compra/",
        detalle_orden_compra,
        name="detalle_orden_compra",
    ),
    path(
        "ordenes-pago/<int:ordenventa_id>/", ver_ordenes_pago, name="ver_ordenes_pago"
    ),
    path(
        "ordenes-pago/filtrar/", ver_ordenes_pago, name="filtrar_ordenes_pago_por_fecha"
    ),
    path('ordenes-pago/detalles-pago/<int:ordenventa_id>/', ver_detalles_pago, name='ver_detalles_pago'),
    path('ordenes-pago/actualizar/<int:pk>/', actualizar_pago, name='actualizar_pago'),

    # cronograma semaforo
    path('cronograma-ordenes-compra/', cronograma_ordenes_compra, name='cronograma_ordenes_compra'),
    


]
