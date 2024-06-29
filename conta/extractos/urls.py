from django.urls import path
from .views import BancoCreateExtracto, BancoListView, BancoCreateView, BancoUpdateView, BancoDeleteView, carga_extracto, extractos_por_banco

urlpatterns = [
    path('', BancoListView.as_view(), name='banco_list'),
    path('create/', BancoCreateView.as_view(), name='banco_create'),
    path('update/<int:pk>/', BancoUpdateView.as_view(), name='banco_update'),
    path('delete/<int:pk>/', BancoDeleteView.as_view(), name='banco_delete'),
    path('extractos/cargar/', BancoCreateExtracto.as_view(), name='cargar_extractos_banco'),

    # extractos bancarios
    path('cargar-extractos/', carga_extracto, name='cargar_extractos'),
    path('bancos/<int:banco_id>/extractos/', extractos_por_banco, name='extractos_por_banco'),
]
