from django.urls import path
from . import views

app_name = "establecimientos"

urlpatterns = [
    path("buscar/",views.buscar,name="buscar"),
    path("crear/",views.crear_establecimiento,name="crear_establecimiento"),
    
]
