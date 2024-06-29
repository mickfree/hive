from django.urls import path, include
from .views import DashboardView, compra_detalle, ingresos_detalle, egresos_detalle, venta_detalle, cuentas_por_cobrar, cuentas_por_pagar

urlpatterns = [
    path('', DashboardView.home, name='home'),
    path('compra-detalle/', compra_detalle, name='compra_detalle'),
    path('ingresos-detalle/', ingresos_detalle, name='ingresos_detalle'),
    path('egresos-detalle/', egresos_detalle, name='egresos_detalle'),
    path('venta-detalle/', venta_detalle, name='venta_detalle'),
    path('cuentas-por-cobrar/', cuentas_por_cobrar, name='cuentas_por_cobrar'),
    path('cuentas-por-pagar/', cuentas_por_pagar, name='cuentas_por_pagar'),
]
