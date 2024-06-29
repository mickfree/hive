from django.urls import path
from . import views
from resources.views import assign_resource

urlpatterns = [
    # ** Order
    path('pruebas/<int:pk>/', views.lista_tarjetas, name='lista_tarjetas'),
    path('cambiar_orden/<int:tarjeta_id>/<int:tarea_id>/<int:nuevo_orden>/', views.cambiar_orden, name='cambiar_orden'),

    # ** Tareas    
    path('newtareas', views.new_lista_tareas, name='new_lista_tareas'),
    path('newtareas/nueva/', views.new_nueva_tarea, name='new_nueva_tarea'),
    path('newtareas/editar/<int:pk>/', views.new_editar_tarea, name='new_editar_tarea'),
    path('newtareas/eliminar/<int:pk>/', views.new_eliminar_tarea, name='new_eliminar_tarea'),
    
    # ** tarjetas
    path('newtarjetas/', views.new_lista_tarjetas, name='new_lista_tarjetas'),
    path('newtarjetas/nueva/', views.new_nueva_tarjeta, name='new_nueva_tarjeta'),
    path('newtarjetas/editar/<int:pk>/', views.new_editar_tarjeta, name='new_editar_tarjeta'),
    path('newtarjetas/eliminar/<int:pk>/', views.new_eliminar_tarjeta, name='new_eliminar_tarjeta'),
    
    # Incidentes
    path('newtarjeta/<int:tarjeta_id>/create_incident/', views.create_incident, name='create_incident'),
    path('descargar_excel/<int:pk>/', views.descargar_excel, name='descargar_excel'),
    path('addresource/<int:tarea_id>/', assign_resource, name='assign_resource'),
]
