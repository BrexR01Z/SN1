from django.urls import path
from . import views

urlpatterns = [
    path("registro/",views.registro,name="Registro"),
    path("login/",views.login,name="Login"),
]