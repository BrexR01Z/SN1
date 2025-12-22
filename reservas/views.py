from django.shortcuts import render, redirect, get_object_or_404
from establecimientos.models import Cancha, Establecimiento
from .models import Reserva, actualizar_estados_reservas_activas
from cuentas.models import Usuario,Dueno
from .forms import CrearReservaForm
from django.contrib import messages
from datetime import datetime, timedelta
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Q
from django.core.exceptions import ValidationError
from establecimientos.models import HorarioEstablecimiento
from django.contrib import messages
from cuentas.models import Usuario, Dueno, Invitation 
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.

def conflicto_hora(reserva):
    inicio = datetime.combine(reserva.fecha, reserva.hora_inicio)
    fin = inicio + timedelta(minutes=reserva.duracion_bloques * 30)
    
    conflictos = Reserva.objects.filter(
        cancha=reserva.cancha,
        fecha=reserva.fecha,
        estado__in=["PENDIENTE", "CONFIRMADA","EN_CURSO"]
    ).exclude(id=reserva.id)
    
    for x in conflictos:
        x_fin = datetime.combine(x.fecha, x.hora_fin())
        if not (fin.time() <= x.hora_inicio or reserva.hora_inicio >= x_fin.time()):
            return True
    return False


@login_required(login_url="cuentas:login_cuenta")
@require_http_methods(["GET", "POST"])
def crear_reserva(request, cancha_id):
    cancha = get_object_or_404(Cancha, id=cancha_id)
    
    reservas_cancha = Reserva.objects.filter(
        cancha=cancha,
        estado__in=["PENDIENTE", "CONFIRMADA","EN_CURSO"]
    ).select_related("usuario").order_by("fecha", "hora_inicio")
    
    horarios = HorarioEstablecimiento.objects.filter(
        establecimiento=cancha.establecimiento
    ).order_by('dia')
    
    if request.method == "POST":
        form = CrearReservaForm(request.POST, cancha=cancha)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.cancha = cancha
            reserva.usuario = request.user

            if conflicto_hora(reserva):
                messages.error(request, "Ya existe una reserva en ese horario")
                return render(request, "crear_reserva.html", {
                    "form": form,
                    "cancha": cancha,
                    "reservas_cancha": reservas_cancha,
                    "horarios": horarios,
                })
            
            reserva.save()
            messages.success(request, "Reserva creada")
            return redirect("cuentas:invitar_a_reserva", reserva_id=reserva.id)
    else:
        form = CrearReservaForm(cancha=cancha)
    
    for reserva in reservas_cancha:
        reserva.hora_fin = reserva.hora_fin()
    
    return render(request, "crear_reserva.html", {
        "form": form,
        "cancha": cancha,
        "reservas_cancha": reservas_cancha,
        "horarios": horarios,
    })

@login_required(login_url="cuentas:login_cuenta")
def listar_reservas(request):

    actualizar_estados_reservas_activas()

    try:
        dueno = Dueno.objects.get(usuario=request.user)
        es_dueno = True
    except Dueno.DoesNotExist:
        es_dueno = False
    
    #  Obtener IDs de reservas donde fui invitado y acepté
    reservas_aceptadas_ids = Invitation.objects.filter(
        receiver=request.user,
        accepted=True,
        reserva__isnull=False  # Solo invitaciones con reserva asociada
    ).values_list('reserva_id', flat=True)
    
    if es_dueno:
        canchas_propias = Cancha.objects.filter(
            establecimiento__dueno=dueno
        ).values_list("id", flat=True)
        
        reservas = Reserva.objects.filter(
            Q(usuario=request.user) | 
            Q(cancha_id__in=canchas_propias) |
            Q(id__in=reservas_aceptadas_ids) 
        ).select_related("usuario", "cancha", "cancha__establecimiento").order_by("-fecha", "-hora_inicio").distinct()
    else:
        reservas = Reserva.objects.filter(
            Q(usuario=request.user) |
            Q(id__in=reservas_aceptadas_ids)  
        ).select_related("cancha", "cancha__establecimiento").order_by("-fecha", "-hora_inicio").distinct()
    
    return render(request, "listar_reservas.html", {
        "reservas": reservas,
        "es_dueno": es_dueno,
    })


def validar_reserva(reserva, cancha, fecha, hora_inicio, duracion_bloques):
    
    if duracion_bloques <= 0:
        return False, "La reserva debe durar como minimo 1 bloque"
    
    if fecha < datetime.now().date():
        return False, "La fecha no puede ser en el pasado"
    
    dias_semana = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
    dia_semana = dias_semana[fecha.weekday()]
    
    horario = HorarioEstablecimiento.objects.filter(
        establecimiento=cancha.establecimiento,
        dia=dia_semana
    ).first()
    
    if not horario:
        return False, f"El establecimiento está cerrado el {dia_semana}"
    
    if hora_inicio < horario.hora_apertura or hora_inicio >= horario.hora_cierre:
        return False, f"La reserva debe estar dentro del horario permitido"
    
    fin = datetime.combine(fecha, hora_inicio) + timedelta(minutes=duracion_bloques * 30)
    if fin.time() > horario.hora_cierre:
        return False, "La reserva debe terminar antes del cierre del establecimiento"
    
    return True, None


@login_required(login_url='cuentas:login_cuenta')
def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.actualizar_estado()
    
    es_propietario = reserva.usuario == request.user
    es_dueno_cancha = False
    
    try:
        dueno = Dueno.objects.get(usuario=request.user)
        es_dueno_cancha = reserva.cancha.establecimiento.dueno == dueno if reserva.cancha else False
    except Dueno.DoesNotExist:
        pass
    
    if not (es_propietario or es_dueno_cancha):
        messages.error(request, "No tienes permiso para editar esta reserva")  
        return redirect('reservas:listar_reservas')  # Cambiado de HttpResponseForbidden
    
    if not reserva.puede_ser_editada():
        messages.error(request, "No puedes editar reservas canceladas o terminadas")
        return redirect('reservas:listar_reservas')
    
    if request.method == 'POST':
        form = CrearReservaForm(request.POST, instance=reserva, cancha=reserva.cancha) 
        if form.is_valid():
            fecha = form.cleaned_data['fecha']
            hora_inicio = form.cleaned_data['hora_inicio']
            duracion_bloques = form.cleaned_data['duracion_bloques']
            
            reserva_temp = Reserva(
                cancha=reserva.cancha,
                fecha=fecha,
                hora_inicio=hora_inicio,
                duracion_bloques=duracion_bloques,
                id=reserva.id 
            )
            
            if conflicto_hora(reserva_temp):
                messages.error(request, "Ya existe una reserva en ese horario")
                return render(request, 'editar_reserva.html', {
                    'form': form,
                    'reserva': reserva,
                    'es_dueno_cancha': es_dueno_cancha,
                })
            
            form.save()
            
            if es_propietario and not es_dueno_cancha:
                reserva.estado = 'PENDIENTE'
                reserva.save()
                messages.success(request, 'Reserva actualizada, espera confirmación')
            elif es_dueno_cancha and 'estado' in request.POST:
                reserva.estado = request.POST['estado']
                reserva.save()
                messages.success(request, 'Reserva actualizada')
            else:
                messages.success(request, 'Reserva actualizada')
            
            return redirect('reservas:listar_reservas')
    else:
        form = CrearReservaForm(instance=reserva, cancha=reserva.cancha)  
    
    return render(request, 'editar_reserva.html', {
        'form': form,
        'reserva': reserva,
        'es_dueno_cancha': es_dueno_cancha,
    })

@login_required(login_url="cuentas:login_cuenta")
@require_http_methods(["GET", "POST"])
def eliminar_reserva(request, reserva_id):
    
    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.actualizar_estado()
    
    es_propietario = reserva.usuario == request.user
    es_dueno_cancha = False
    
    try:
        dueno = Dueno.objects.get(usuario=request.user)
        es_dueno_cancha = reserva.cancha.establecimiento.dueno == dueno
    except Dueno.DoesNotExist:
        pass
    
    if not (es_propietario or es_dueno_cancha):
        messages.error(request, "Solo el anfitrión o dueño del establecimiento puede cancelar esta reserva")
        return redirect('reservas:listar_reservas')
    
    if not reserva.puede_ser_cancelada():
        messages.error(request, "No puedes cancelar una reserva ya terminada o cancelada")
        return redirect('reservas:listar_reservas')

    if request.method == "POST":
        # Guardar info antes de cancelar
        info_reserva = {
            'cancha': reserva.cancha.nombre,
            'establecimiento': reserva.cancha.establecimiento.nombre,
            'fecha': reserva.fecha.strftime('%d/%m/%Y'),
            'hora_inicio': reserva.hora_inicio.strftime('%H:%M'),
            'hora_fin': reserva.hora_fin().strftime('%H:%M'),  # ← hora_fin() con paréntesis porque es un método
            'cancelado_por': request.user.get_full_name() or request.user.username,
        }
        
        # Recopilar emails de participantes
        participantes_emails = []
        
        # 1. Email del anfitrión (dueño de la reserva)
        if reserva.usuario.email:
            participantes_emails.append(reserva.usuario.email)
        
        # 2. Emails de invitados que aceptaron
        invitaciones_aceptadas = reserva.invitaciones.filter(accepted=True)
        for invitacion in invitaciones_aceptadas:
            if invitacion.receiver.email:
                participantes_emails.append(invitacion.receiver.email)
        
        # Eliminar invitaciones pendientes (no aceptadas)
        invitaciones_pendientes = reserva.invitaciones.filter(accepted=False)
        cantidad_eliminadas = invitaciones_pendientes.count()
        invitaciones_pendientes.delete()
        
        if cantidad_eliminadas > 0:
            print(f"Se eliminaron {cantidad_eliminadas} invitaciones pendientes")
        
        # Cancelar la reserva
        reserva.estado = 'CANCELADA'
        reserva.save()
        
        # Enviar emails
        if participantes_emails:
            try:
                enviar_emails_cancelacion(participantes_emails, info_reserva)
                messages.success(
                    request, 
                    f"Reserva cancelada correctamente. Se enviaron {len(participantes_emails)} notificaciones por email."
                )
            except Exception as e:
                messages.warning(
                    request,
                    f"Reserva cancelada correctamente, pero hubo un error al enviar algunos emails: {str(e)}"
                )
        else:
            messages.success(request, "Reserva cancelada correctamente")
        
        return redirect("reservas:listar_reservas")
    
    return render(request, "eliminar_reserva.html", {
        "reserva": reserva,
    })


def enviar_emails_cancelacion(emails_list, info_reserva): #Envía mails de cancelación de reserva todos a los participantes.
    subject = f"[NOTIFICACIÓN] Reserva Cancelada - {info_reserva['cancha']}"
    
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
                background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
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
            .warning-box {{
                background: #7f1d1d;
                border-left: 4px solid #ef4444;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
            }}
            .warning-box strong {{
                color: #fca5a5;
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
                color: #60a5fa;
                font-weight: 700;
            }}
            .message {{
                color: #d1d5db;
                line-height: 1.7;
                margin: 20px 0;
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
                <h1>Reserva Cancelada</h1>
                <p>Tu reserva ha sido cancelada</p>
            </div>
            
            <div class="content">
                <div class="warning-box">
                    <strong>La siguiente reserva ha sido cancelada</strong>
                </div>
                
                <div class="info-box">
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
                        <span class="label">Cancelado por:</span>
                        <span class="value">{info_reserva['cancelado_por']}</span>
                    </div>
                </div>
                
                <p class="message">
                    Lamentamos los inconvenientes. Puedes hacer una nueva reserva en cualquier momento desde nuestra plataforma.
                </p>
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
    RESERVA CANCELADA - SPORTSNET
    
    La siguiente reserva ha sido cancelada:
    
    Cancha: {info_reserva['cancha']}
    Establecimiento: {info_reserva['establecimiento']}
    Fecha: {info_reserva['fecha']}
    Horario: {info_reserva['hora_inicio']} - {info_reserva['hora_fin']}
    Cancelado por: {info_reserva['cancelado_por']}
    
    Lamentamos los inconvenientes.
    Puedes hacer una nueva reserva en cualquier momento.
    
    ---
    SportsNet - Sistema de Reservas Deportivas
    Este es un email automático, por favor no respondas a este correo.
    """
    
    # Enviar email a cada participante
    emails_enviados = 0
    for email in emails_list:
        if email:  # Verificar que el email no esté vacío
            try:
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=False,
                )
                emails_enviados += 1
            except Exception as e:
                print(f"Error enviando email a {email}: {str(e)}")
    
    print(f"{emails_enviados}/{len(emails_list)} emails enviados exitosamente")
    return emails_enviados