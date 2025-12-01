from django.urls import path
from . import views

app_name = "establecimientos"

urlpatterns = [
    #  canchas
    path("buscar/",views.buscar,name="buscar"),
    path("<int:establecimiento_id>/canchas/crear", views.crear_cancha, name="crear_cancha"),
    path("canchas/<int:cancha_id>", views.ver_cancha, name = "ver_cancha"),
    

    # establecimiento
    path("crear/",views.crear_establecimiento,name="crear_establecimiento"),
    path("ver/<int:establecimiento>",views.ver_establecimiento,name="ver_establecimiento"),
    path('<int:establecimiento_id>/editar/', views.editar_establecimiento, name='editar_establecimiento'),
    path('<int:establecimiento_id>/eliminar/', views.eliminar_establecimiento, name='eliminar_establecimiento'),


    
    
]
