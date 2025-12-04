from django.shortcuts import render, redirect,  get_object_or_404 # Importar get_object_or_404
from .forms import RegistroForm # Importar el formulario de registro
from django.template import loader # Importar el cargador de plantillas
from django.http import HttpResponse, HttpResponseRedirect # Importar HttpResponseRedirect
from .models import Usuario,Cliente,Dueno # Importar los modelos Usuario, Cliente y Dueño
from django.contrib import messages # Importar el sistema de mensajes
from django.contrib.auth import authenticate, login, logout, get_user_model # Importar get_user_model
from django.contrib.auth.decorators import login_required # Importar el decorador login_required
from django.db import transaction # Importar transaction para manejo de transacciones
from django.urls import reverse # Importar reverse
from django.core.mail import send_mail # Importar la función para enviar correos
from django.conf import settings # Importar la configuración de correo
from .models import Invitation # Modelo de invitación
from .forms import InvitationForm # Formulario de invitación
from .forms import EditarPerfilForm # Formulario para editar el perfil de usuario
from django.db.models import Q
from .models import Usuario
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from reservas.models import Reserva

# Create your views here.

def registro(request):
    template = loader.get_template("registro.html")
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():    
            usuario = form.save()
            tipo_usuario = form.cleaned_data["tipo_usuario"]

            if tipo_usuario == "dueno":
                Dueno.objects.create(usuario = usuario, rut = form.cleaned_data["rut"])
                login(request, usuario)
                return redirect ("cuentas:SportsNet_dueno")
                
                
            else:                        
                Cliente.objects.create(usuario=usuario)
                login(request, usuario)
                return redirect ("cuentas:SportsNet_cliente")
   

    else:
        form = RegistroForm()

    context = {
        "form" : form
    }

    return render (request, "registro.html", context)

def login_cuenta(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
     
        user = authenticate(request, username=username, password=password)
        

        if user is not None:
            
            login(request, user)
            
            # messages.success(request, f"Sesión iniciada correctamente, Bienvenido {user.username}")
            try:
                dueno = request.user.perfil_dueno
                return redirect ("cuentas:SportsNet_dueno")
            except:
                return redirect ("cuentas:SportsNet_cliente")


        else:
            messages.error(request, "Usuario o contraseña incorrectos")
            return redirect ("cuentas:login_cuenta")
            
    """
    context = {
        "user":user,
    }
    """

    return render (request, "login.html")

def home (request):
    return render(request,"home.html")

@login_required(login_url='cuentas:login_cuenta')
def cerrar_sesion(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente')
    return redirect("cuentas:home")

@login_required(login_url='cuentas:login_cuenta')
def bienvenida_dueno(request):
    try:
        dueno = request.user.perfil_dueno
    except:
        # messages.error (request, "Debe ser usuario dueno")
        return redirect ("cuentas:home")
    
    establecimientos = dueno.establecimientos.all()
    canchas = sum(est.canchas.count() for est in establecimientos)
    
    context = {
        "dueno" : dueno,
        "establecimientos" : establecimientos,
        "canchas": canchas
    }

    return render(request,"bienvenida_dueno.html", context)

@login_required(login_url='cuentas:login_cuenta')
def bienvenida_cliente(request):
    try:
        cliente = request.user.perfil_cliente
    except:
        return redirect ("cuentas:home")
    
    # reservas = cliente.reservas.all()
    
    
    context = {
        "cliente" : cliente,
        # "reservas" : reservas,
        
    }

    return render(request,"bienvenida_cliente.html", context)

#===============================INVITACIONES DE USUARIOS==================================

# VISTA PARA INVITAR A UN USUARIO A UNA PARTIDA. 

def invitar_usuario(request):
    return HttpResponse("Página de invitar usuario — aún en construcción")

def aceptar_invitacion(request, id):
    return HttpResponse(f"Aceptar invitación #{id} — en construcción")

def rechazar_invitacion(request, id):
    return HttpResponse(f"Rechazar invitación #{id} — en construcción")

# VISTA DE PRUEBA PARA ENVÍO DE CORREOS [SOLO PARA TESTEO!!!!!!!]

def test_email(request): # PRUEBA PARA ENVÍO DE CORREOS [SOLO PARA TESTEO!!!!]
    send_mail(
        subject="Prueba de correo",
        message="Este es un mensaje de prueba enviado desde Django.",
        from_email=None,  # usa DEFAULT_FROM_EMAIL
        recipient_list=["tu_correo@ejemplo.com"],
    )
    return HttpResponse("Correo enviado (revisar consola)")


User = get_user_model()

@login_required
def invitar_usuario(request):
    if request.method == "POST":
        form = InvitationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]

            # ¿Existe el usuario?
            try:
                receiver = User.objects.get(username=username)
            except User.DoesNotExist:
                messages.error(request, "Ese usuario no existe.")
                return redirect("cuentas:invitar_usuario")


            # ¿Es él mismo?
            if receiver == request.user:
                messages.error(request, "No puedes invitarte a ti mismo.")
                return redirect("cuentas:invitar_usuario")


            # ¿Ya existe una invitación pendiente?
            existing = Invitation.objects.filter(
                sender=request.user,
                receiver=receiver,
                accepted=False,
            ).exists()

            if existing:
                messages.warning(request, "Ya enviaste una invitación pendiente a este usuario.")
                return redirect("cuentas:invitar_usuario")


           # Crear invitación
            invitacion = Invitation.objects.create(
                sender=request.user,
                receiver=receiver
            )

            #  ENVIAR CORREO AQUÍ MISMO
            send_mail(
                subject="¡Tienes una nueva invitación en LifeSportsNet!",
                message=f"El usuario {request.user.username} te ha enviado una invitación.\n\n"
                        f"Para aceptarla o rechazarla, ingresa a alguno de los siguientes enlaces con la sesión iniciada:\n"
                        f"Aceptar: {request.build_absolute_uri(reverse('cuentas:aceptar_invitacion', args=[invitacion.id]))}\n"
                        f"Rechazar: {request.build_absolute_uri(reverse('cuentas:rechazar_invitacion', args=[invitacion.id]))}\n\n"
                        f"¡Gracias por usar LifeSportsNet!",

                from_email="noreply@sportsnet.cl",
                recipient_list=[receiver.email],
                fail_silently=False,
            )

            messages.success(request, "Invitación enviada y correo enviado correctamente.")
            return redirect("cuentas:invitar_usuario")

    else:
        form = InvitationForm()

    return render(request, "invitar_usuario.html", {"form": form})

User = get_user_model()

@login_required(login_url='cuentas:login_cuenta')
@login_required(login_url='cuentas:login_cuenta')
def invitar_a_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    # Sólo el creador de la reserva puede invitar (mínimo check de seguridad)
    if reserva.usuario != request.user:
        messages.error(request, "No puedes invitar a esta reserva (no eres el creador).")
        return redirect("cuentas:perfil_usuario")

    if request.method == "POST":
        form = InvitationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            # buscar receptor
            try:
                receiver = User.objects.get(username=username)
            except User.DoesNotExist:
                messages.error(request, "Ese usuario no existe.")
                return redirect("cuentas:invitar_a_reserva", reserva_id=reserva.id)

            if receiver == request.user:
                messages.error(request, "No puedes invitarte a ti mismo.")
                return redirect("cuentas:invitar_a_reserva", reserva_id=reserva.id)

            # chequeo duplicado (misma reserva, misma invitación pendiente)
            existing = Invitation.objects.filter(
                sender=request.user,
                receiver=receiver,
                reserva=reserva,
                accepted=False
            ).exists()

            if existing:
                messages.warning(request, "Ya enviaste una invitación pendiente a este usuario para esta reserva.")
                return redirect("cuentas:invitar_a_reserva", reserva_id=reserva.id)

            # crear invitación vinculada a reserva
            Invitation.objects.create(
                sender=request.user,
                receiver=receiver,
                reserva=reserva
            )

            # (Opcional) enviar correo similar al flujo actual — omito el envío para mantenerlo simple
            send_mail(
                subject="¡Tienes una nueva invitación en SportsNet!",
                message=f"El usuario {request.user.username} te ha enviado una invitación.\n\n"
                        f"Para aceptarla o rechazarla, ingresa al siguiente enlace con la sesión iniciada:\n"
                        f"Ver Invitaciones: {request.build_absolute_uri(reverse('cuentas:perfil_usuario'))}\n\n"
                        f"¡Gracias por usar SportsNet!",

                from_email="noreply@sportsnet.cl",
                recipient_list=[receiver.email],
                fail_silently=False,
            )
            
            messages.success(request, f"Invitación enviada a {receiver.username} para la reserva.")
            return redirect("cuentas:invitar_a_reserva", reserva_id=reserva.id)
    else:
        form = InvitationForm()

    # Obtener todas las invitaciones de esta reserva
    invitaciones = Invitation.objects.filter(
        reserva=reserva,
        sender=request.user
    ).select_related('receiver').order_by('-created_at')

    return render(request, "invitar_a_reserva.html", {
        "form": form, 
        "reserva": reserva,
        "invitaciones": invitaciones
    })
@login_required
def aceptar_invitacion(request, id):
    try:
        invitacion = Invitation.objects.get(id=id, receiver=request.user)
    except Invitation.DoesNotExist:
        messages.error(request, "Invitación no encontrada.")
        return redirect("cuentas:perfil_usuario")

    invitacion.accepted = True
    invitacion.save()

    messages.success(request, "Invitación aceptada.")
    return redirect("cuentas:perfil_usuario")


@login_required
def rechazar_invitacion(request, id):
    try:
        invitacion = Invitation.objects.get(id=id, receiver=request.user)
    except Invitation.DoesNotExist:
        messages.error(request, "Invitación no encontrada.")
        return redirect("cuentas:perfil_usuario")

    invitacion.accepted = False
    invitacion.save()

    messages.success(request, "Invitación rechazada.")
    return redirect("cuentas:perfil_usuario")


# VISTA DE PRUEBA PARA CREAR INVITACIÓN Y MOSTRAR LINKS
def test_invite(request):
    sender = User.objects.get(username="antonio")  
    receiver = User.objects.get(username="amigo")  

    invitation = Invitation.objects.create(
        sender=sender,
        receiver=receiver
    )

    accept_url = request.build_absolute_uri(
        reverse('aceptar_invitacion', args=[invitation.id])
    )

    reject_url = request.build_absolute_uri(
        reverse('rechazar_invitacion', args=[invitation.id])
    )

    return HttpResponse(
        f"Invitación creada.<br>"
        f"Aceptar: {accept_url}<br>"
        f"Rechazar: {reject_url}"
    )

#==============================FIN INVITACIONES DE USUARIOS==================================
#==============================PERFIL DE USUARIO==================================
@login_required
def perfil_usuario(request):
    usuario = request.user
    
    # Invitaciones recibidas (pendientes)
    invitaciones = Invitation.objects.filter(receiver=usuario, accepted=False)

    return render(request, "perfil_usuario.html", {
        "usuario": usuario,
        "invitaciones": invitaciones,
    })

@login_required
def editar_perfil(request):
    usuario = request.user

    if request.method == "POST":
        form = EditarPerfilForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("cuentas:perfil_usuario")
    else:
        form = EditarPerfilForm(instance=usuario)

    return render(request, "editar_perfil.html", {"form": form})

@login_required
def buscar_perfiles(request): # Vista para buscar otros perfiles de usuario
    query = request.GET.get("q", "")
    resultados = []

    if query:
        resultados = Usuario.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query)
        )

    return render(request, "buscar_perfiles.html", {
        "query": query,
        "resultados": resultados
    })

@login_required
def ver_perfil_publico(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    return render(request, "ver_perfil_publico.html", {"usuario": usuario})


#==============================FIN PERFIL DE USUARIO==================================