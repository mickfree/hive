from django.urls import include, path
from .views import crear_proceso, mi_vista_compleja, lista_procesos, lista_subprocesos, lista_tareas, eliminar_proceso # Asegúrate de importar la vista correctamente
from . import views

urlpatterns = [
    path('procesos/', mi_vista_compleja, name='procesos_sin_id'),
    path('procesos/<int:proceso_id>/<int:subproceso_id>/', mi_vista_compleja, name='procesos_con_id'),
    path('procesos/<int:proceso_id>/', mi_vista_compleja, name='procesos_con_id'),

    #metodos de procesos
    path('lista_procesos/', lista_procesos, name='lista_procesos'),
    path('eliminar_proceso/<int:proceso_id>/', eliminar_proceso, name='eliminar_proceso'),
    #path('proceso/<int:proceso_id>/editar/', views.editar_proceso, name='editar_proceso'),
    path('proceso/<int:proceso_id>/editar/', views.editar_proceso, name='editar_proceso'),

    #lista de subprocesos
    path('lista_subprocesos/', lista_subprocesos, name='lista_subprocesos'),
    path('subproceso/<int:subproceso_id>/editar/', views.editar_subproceso, name='editar_subproceso'),

    #lista de tareas
    path('lista_tareas/', lista_tareas, name='lista_tareas'),

    # urls para la creacion de procesos, subproceso y tareas
    path('crear-proceso/', crear_proceso, name='crear_proceso'),
    path('proceso/<int:proceso_id>/', views.ver_proceso, name='ver_proceso'),
    path('subproceso/<int:subproceso_id>/', views.ver_subproceso, name='ver_subproceso'),
]
