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

def home(request):
    context = {}
    
    if request.user.is_authenticated:
        # Buscar invitaciones pendientes (con el nuevo campo status)
        invitacion_pendiente = request.user.received_invitations.filter(
            status='pending'  # ← CAMBIO AQUÍ
        ).order_by('-created_at').first()
        
        context['invitacion_pendiente'] = invitacion_pendiente
    
    return render(request, 'home.html', context)

@login_required
def SportsNet_cliente(request):
    cliente = request.user.perfil_cliente
    
    # Buscar invitación pendiente
    invitacion_pendiente = request.user.received_invitations.filter(
        status='pending'  # ← CAMBIO AQUÍ
    ).order_by('-created_at').first()
    
    context = {
        'cliente': cliente,
        'invitacion_pendiente': invitacion_pendiente
    }
    
    return render(request, 'cuentas/bienvenida_cliente.html', context)

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

# VISTA DE PRUEBA PARA ENVÍO DE CORREOS [SOLO PARA TESTEO!!!!!!!]

def test_email(request): # PRUEBA PARA ENVÍO DE CORREOS [SOLO PARA TESTEO!!!!]
    send_mail(
        subject="Prueba de correo",
        message="Este es un mensaje de prueba enviado desde Django.",
        from_email=None,  # usa DEFAULT_FROM_EMAIL
        recipient_list=["tu_correo@ejemplo.com"],
    )
    return HttpResponse("Correo enviado (revisar consola)")


def enviar_email_invitacion(receiver_email, sender_username, reserva, url_invitaciones):
    """Envía email de invitación a reserva con diseño moderno"""
    
    # Preparar información de la reserva
    info_reserva = {
        'cancha': reserva.cancha.nombre if reserva.cancha else 'Cancha no disponible',
        'establecimiento': reserva.cancha.establecimiento.nombre if reserva.cancha else 'Establecimiento no disponible',
        'deporte': reserva.cancha.get_deporte_display() if reserva.cancha else '---',
        'fecha': reserva.fecha.strftime('%d/%m/%Y'),
        'hora_inicio': reserva.hora_inicio.strftime('%H:%M'),
        'hora_fin': reserva.hora_fin().strftime('%H:%M'),
        'precio_total': f"${int(reserva.precio_total):,}" if reserva.precio_total else "N/A",
    }
    
    subject = f"[INVITACIÓN] Nueva invitación a reserva - {info_reserva['cancha']}"
    
    # Email en HTML
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background-color: #000000;
                margin: 0;
                padding: 0;
                color: #d1d5db;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
                border: 2px solid #374151;
            }}
            .header {{
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 800;
            }}
            .header p {{
                margin: 10px 0 0 0;
                opacity: 0.9;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .invitation-box {{
                background: #064e3b;
                border-left: 4px solid #10b981;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
            }}
            .invitation-box strong {{
                color: #6ee7b7;
                font-size: 16px;
            }}
            .info-box {{
                background: #1f2937;
                border-radius: 12px;
                padding: 20px;
                margin: 25px 0;
                border: 1px solid #374151;
            }}
            .info-row {{
                display: flex;
                justify-content: space-between;
                padding: 12px 0;
                border-bottom: 1px solid #374151;
            }}
            .info-row:last-child {{
                border-bottom: none;
            }}
            .label {{
                color: #9ca3af;
                font-weight: 500;
            }}
            .value {{
                color: #34d399;
                font-weight: 700;
            }}
            .message {{
                color: #d1d5db;
                line-height: 1.7;
                margin: 20px 0;
            }}
            .cta-button {{
                display: inline-block;
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                padding: 16px 32px;
                text-decoration: none;
                border-radius: 10px;
                font-weight: 700;
                font-size: 16px;
                margin: 20px 0;
                box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
                transition: transform 0.2s;
            }}
            .cta-button:hover {{
                transform: translateY(-2px);
            }}
            .button-container {{
                text-align: center;
                margin: 30px 0;
            }}
            .footer {{
                background: #0f172a;
                padding: 25px;
                text-align: center;
                color: #6b7280;
                font-size: 14px;
                border-top: 1px solid #374151;
            }}
            .footer p {{
                margin: 5px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>¡Nueva Invitación!</h1>
                <p>Te han invitado a una reserva deportiva</p>
            </div>
            
            <div class="content">
                <div class="invitation-box">
                    <strong>{sender_username}</strong> te ha invitado a unirte a su reserva
                </div>
                
                <div class="info-box">
                    <div class="info-row">
                        <span class="label">Deporte:</span>
                        <span class="value">{info_reserva['deporte']}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Cancha:</span>
                        <span class="value">{info_reserva['cancha']}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Establecimiento:</span>
                        <span class="value">{info_reserva['establecimiento']}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Fecha:</span>
                        <span class="value">{info_reserva['fecha']}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Horario:</span>
                        <span class="value">{info_reserva['hora_inicio']} - {info_reserva['hora_fin']}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Precio Total:</span>
                        <span class="value">{info_reserva['precio_total']}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Invitado por:</span>
                        <span class="value">{sender_username}</span>
                    </div>
                </div>
                
                <p class="message">
                    Para aceptar o rechazar esta invitación, haz clic en el botón de abajo. 
                    Recuerda que debes tener la sesión iniciada en SportsNet.
                </p>
                
                <div class="button-container">
                    <a href="{url_invitaciones}" class="cta-button">
                        Ver Mis Invitaciones
                    </a>
                </div>
            </div>
            
            <div class="footer">
                <p><strong>SportsNet</strong> - Sistema de Reservas Deportivas</p>
                <p>Este es un email automático, por favor no respondas a este correo</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Email en texto plano (fallback)
    plain_message = f"""
    ¡NUEVA INVITACIÓN! - SPORTSNET
    
    {sender_username} te ha invitado a unirte a su reserva:
    
    Deporte: {info_reserva['deporte']}
    Cancha: {info_reserva['cancha']}
    Establecimiento: {info_reserva['establecimiento']}
    Fecha: {info_reserva['fecha']}
    Horario: {info_reserva['hora_inicio']} - {info_reserva['hora_fin']}
    Precio Total: {info_reserva['precio_total']}
    
    Para aceptar o rechazar esta invitación, ingresa al siguiente enlace:
    {url_invitaciones}
    
    (Recuerda tener la sesión iniciada en SportsNet)
    
    ---
    SportsNet - Sistema de Reservas Deportivas
    Este es un email automático, por favor no respondas a este correo.
    """
    
    # Enviar email
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[receiver_email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"Email de invitación enviado exitosamente a {receiver_email}")
        return True
    except Exception as e:
        print(f"Error enviando email de invitación a {receiver_email}: {str(e)}")
        return False

User = get_user_model()

@login_required(login_url='cuentas:login_cuenta')
def invitar_a_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if reserva.usuario != request.user:
        messages.error(request, "No puedes invitar a esta reserva (no eres el creador).")
        return redirect("cuentas:perfil_usuario")

    if request.method == "POST":
        form = InvitationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            try:
                receiver = User.objects.get(username=username)
            except User.DoesNotExist:
                messages.error(request, "Ese usuario no existe.")
                return redirect("cuentas:invitar_a_reserva", reserva_id=reserva.id)

            if receiver == request.user:
                messages.error(request, "No puedes invitarte a ti mismo.")
                return redirect("cuentas:invitar_a_reserva", reserva_id=reserva.id)

            existing = Invitation.objects.filter(
                sender=request.user,
                receiver=receiver,
                reserva=reserva,
                status='pending'
            ).exists()

            if existing:
                messages.warning(request, "Ya enviaste una invitación pendiente a este usuario para esta reserva.")
                return redirect("cuentas:invitar_a_reserva", reserva_id=reserva.id)

            # Crear invitación
            Invitation.objects.create(
                sender=request.user,
                receiver=receiver,
                reserva=reserva
            )

            # URL para ver invitaciones
            url_invitaciones = request.build_absolute_uri(
                reverse('cuentas:SportsNet_cliente')
            )

            # Enviar email con el nuevo diseño
            enviar_email_invitacion(
                receiver_email=receiver.email,
                sender_username=request.user.username,
                reserva=reserva,  # Ahora pasamos el objeto reserva completo
                url_invitaciones=url_invitaciones
            )
            
            messages.success(request, f"Invitación enviada a {receiver.username} para la reserva.")
            return redirect("cuentas:invitar_a_reserva", reserva_id=reserva.id)
    else:
        form = InvitationForm()

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
        invitacion = Invitation.objects.get(
            id=id, 
            receiver=request.user,
            status='pending'  # ← AGREGAR ESTE FILTRO
        )
    except Invitation.DoesNotExist:
        messages.error(request, "Invitación no encontrada.")
        return redirect("cuentas:perfil_usuario")

    invitacion.status = 'accepted'  # ← CAMBIO AQUÍ
    invitacion.accepted = True  # Mantener por compatibilidad
    invitacion.save()

    messages.success(request, f"¡Invitación aceptada! La reserva de {invitacion.reserva.cancha.nombre} ya está en 'Mis Reservas'.")
    return redirect("cuentas:perfil_usuario")



@login_required
def rechazar_invitacion(request, id):
    try:
        invitacion = Invitation.objects.get(
            id=id, 
            receiver=request.user,
            status='pending'  # ← AGREGAR ESTE FILTRO
        )
    except Invitation.DoesNotExist:
        messages.error(request, "Invitación no encontrada.")
        return redirect("cuentas:perfil_usuario")

    invitacion.status = 'rejected'  # ← CAMBIO AQUÍ (esto era el problema principal)
    invitacion.save()

    messages.success(request, "¡Invitación rechazada!")
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
    invitaciones = Invitation.objects.filter(
        receiver=usuario, 
        status='pending'  # ← CAMBIO AQUÍ
    )

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

def custom_404 (request,exception):
    return render(request, "404.html", status=404)
