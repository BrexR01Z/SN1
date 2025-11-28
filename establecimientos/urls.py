from django.urls import path
from . import views

app_name = "establecimientos"

urlpatterns = [
    path("buscar/",views.buscar,name="buscar"),
    path("crear/",views.crear_establecimiento,name="crear_establecimiento"),
    path("ver/<int:establecimiento>",views.ver_establecimiento,name="ver_establecimiento"),
    path("<int:establecimiento_id>/canchas/crear", views.crear_cancha, name="crear_cancha"),
]
