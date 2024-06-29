from django.urls import path
from . import views
from .views import inventario, AgregarItemInventario, procesar_excel

urlpatterns = [
    path('inventario/', inventario, name='inventario'),
    path('agregar-item/', AgregarItemInventario.as_view(), name='agregar_item_inventario'),
    path('procesar_excel/', procesar_excel, name='procesar_excel'),

]