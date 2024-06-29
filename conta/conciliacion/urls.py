from django.urls import path
from .views import conciliacion

urlpatterns = [
    path('', conciliacion, name="conciliacion")
]