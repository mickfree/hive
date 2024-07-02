from django.urls import path
from .views import CalendarioMesView, InformeTarjetasMesView, add_task, monthly_tasks, pending_tasks, tarjeta_usuario_dia, crear_tarjeta_para_usuario, ver_tarjeta_equipo, eliminar_tarjeta

urlpatterns = [
     path('calendario-mes/', CalendarioMesView.as_view(), name='calendario-mes'),
     path('informe-tarjetas-mes/', InformeTarjetasMesView.as_view(), name='informe-tarjetas-mes'),
     path('tarjeta-usuario/<int:usuario_id>/<int:dia>/', tarjeta_usuario_dia, name='tarjeta_usuario_dia'),
     path('eliminar-tarjeta/<int:usuario_id>/<int:dia>/', eliminar_tarjeta, name='eliminar_tarjeta'),
     path('crear-tarjeta/<int:usuario_id>/<int:dia>/<str:mes>/<int:anio>/', crear_tarjeta_para_usuario, name='crear_tarjeta_para_usuario'),
     path('informe/<int:anio>/<int:mes>/', InformeTarjetasMesView.as_view(), name='informe_tarjetas_mes'),
     path('ver-tarjeta-equipo/', ver_tarjeta_equipo, name='ver_tarjeta_equipo'),
     # backlog
     path('pending_tasks/', pending_tasks, name='pending_tasks'),
     path('monthly_tasks/<int:mes>/<int:anio>/', monthly_tasks, name='monthly_tasks'),
     path('add_task/<int:backlog_id>/', add_task, name='add_task'),
]
