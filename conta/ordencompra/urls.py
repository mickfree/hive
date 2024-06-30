from django.urls import path
from ordenventa.views import ver_ordenes_pago
from .views import (
    cronograma_ordenes_compra,
    lista_ordenes_compra,
    ver_detalles_pago,
    actualizar_pago
)

urlpatterns = [
    path("", lista_ordenes_compra, name="lista_ordenes_venta"),
    path(
        "ordenes-pago/<int:ordenventa_id>/", ver_ordenes_pago, name="ver_ordenes_pago"
    ),
    path("ordenes-pago/", ver_ordenes_pago, name="ver_todas_ordenes_pago"),
    path(
        "ordenes-pago/filtrar/", ver_ordenes_pago, name="filtrar_ordenes_pago_por_fecha"
    ),
    path('ordenes-pago/detalles-pago/<int:ordenventa_id>/', ver_detalles_pago, name='ver_detalles_pago'),
    path('ordenes-pago/actualizar/<int:pk>/', actualizar_pago, name='actualizar_pago'),

    # cronograma semaforo
    path('cronograma-ordenes-compra/', cronograma_ordenes_compra, name='cronograma_ordenes_compra'),
    


]
