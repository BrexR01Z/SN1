from django.urls import path
from . import views

app_name = "establecimientos"

urlpatterns = [
    #  canchas

    path("cancha/buscar",views.buscar_canchas,name="buscar_canchas"),   
    path("cancha/<int:cancha_id>", views.ver_cancha, name = "ver_cancha"),
    path('cancha/editar/<int:cancha_id>', views.editar_cancha, name='editar_cancha'),
    path('cancha/eliminar/<int:cancha_id>', views.eliminar_cancha, name='eliminar_cancha'),
    

    path("<int:establecimiento_id>/canchas/crear", views.crear_cancha, name="crear_cancha"),

    # establecimiento
    path("establecimiento/crear/",views.crear_establecimiento,name="crear_establecimiento"),
    path("establecimiento/ver/<int:establecimiento>",views.ver_establecimiento,name="ver_establecimiento"),
    path('establecimiento/editar<int:establecimiento_id>', views.editar_establecimiento, name='editar_establecimiento'),
    path('establecimiento/eliminar/<int:establecimiento_id>', views.eliminar_establecimiento, name='eliminar_establecimiento'),


    
    
]
