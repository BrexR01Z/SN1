from django.urls import path
from . import views

app_name = "cuentas"

urlpatterns = [
    path("registro/",views.registro,name="registro"),
    path("login/",views.login_cuenta,name="login_cuenta"),
    path("",views.home,name="home"),
    path("logout/",views.cerrar_sesion,name="cerrar_sesion"),
    path("SportsNet_Dueno/",views.bienvenida_dueno,name="SportsNet_dueno"),
    path("SportsNet_cliente/",views.bienvenida_cliente,name="SportsNet_cliente"),

    #Acceso a la vista de perfil de usuario
    path("perfil/", views.perfil_usuario, name="perfil_usuario"), # Vista para ver y editar el perfil de usuario
    path("perfil/editar/", views.editar_perfil, name="editar_perfil"), # Vista para editar el perfil de usuario
    path("buscar-perfiles/", views.buscar_perfiles, name="buscar_perfiles"), # Vista para buscar otros perfiles de usuario
    path("perfil/<int:id>/", views.ver_perfil_publico, name="ver_perfil_publico"), 



    
    #Acceso a las vistas de aceptar y rechazar invitaciones
    path("invitar/", views.invitar_usuario, name="invitar_usuario"), # Vista para enviar invitaciones
    path('invitar/aceptar/<int:id>/', views.aceptar_invitacion, name='aceptar_invitacion'), # Vista para aceptar invitaciones
    path('invitar/rechazar/<int:id>/', views.rechazar_invitacion, name='rechazar_invitacion'), # Vista para rechazar invitaciones

    #Vistas de prueba para testeo de correos e invitaciones
    path("test-email/", views.test_email, name="test_email"), # VISTA DE PRUEBA PARA ENVÍO DE CORREOS [SOLO PARA TESTEO!!!!]
    path('test-invite/', views.test_invite, name="test_invite"), # VISTA DE PRUEBA PARA INVITACIONES [SOLO PARA TESTEO!!!!]

    

]