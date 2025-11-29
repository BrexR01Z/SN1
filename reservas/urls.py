from django.urls import path
from . import views

app_name = "reservas"

urlpatterns = [
    path("cancha/<int:cancha_id>/crear", views.crear_reserva , name="crear_reserva"),
]