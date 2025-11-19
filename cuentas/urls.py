from django.urls import path
from . import views

app_name = "cuentas"

urlpatterns = [
    path("registro/",views.registro,name="registro"),
    path("login/",views.login_cuenta,name="login_cuenta"),
    path("",views.home,name="home"),
    path("logout/",views.cerrar_sesion,name="cerrar_sesion"),
]