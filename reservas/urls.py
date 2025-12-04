from django.urls import path
from . import views

app_name = "reservas"

urlpatterns = [
    path("cancha/<int:cancha_id>/crear/reservas", views.crear_reserva , name="crear_reserva"),
    path('reservas/', views.listar_reservas, name='listar_reservas'),
    path('<int:reserva_id>/editar/reservas', views.editar_reserva, name='editar_reserva'),
    path('<int:reserva_id>/eliminar/reservas', views.eliminar_reserva, name='eliminar_reserva'),





]