from django.urls import include, path
from .views import planning_homepage


urlpatterns = [
    path('/', planning_homepage, name='planning_homepage')
]