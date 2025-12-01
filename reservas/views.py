from django.shortcuts import render, redirect, get_object_or_404
from establecimientos.models import Cancha, Establecimiento
from .models import Reserva
from cuentas.models import Usuario,Dueno
from .forms import CrearReservaForm
from django.contrib import messages
from datetime import datetime, timedelta
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Q
# Create your views here.


@login_required(login_url="cuentas:login_cuenta")
@require_http_methods(["GET", "POST"])
def crear_reserva(request, cancha_id):
    cancha = get_object_or_404(Cancha, id=cancha_id)
    
    reservas_cancha = Reserva.objects.filter(
        cancha=cancha,
        estado__in=["PENDIENTE", "CONFIRMADA"]
    ).select_related("usuario").order_by("fecha", "hora_inicio")
    
    if request.method == "POST":
        form = CrearReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.cancha = cancha
            reserva.usuario = request.user
            
            if conflicto_hora(reserva):
                messages.error(request, "Ya existe una reserva en ese horario")
            else:
                reserva.save()
                messages.success(request, "Reserva creada")
                return redirect('cuentas:invitar_a_reserva', reserva.id)
                # redirigir a detalles reserva
                #return redirect('reservas:ver_reserva', id=reserva.id)
    else:
        form = CrearReservaForm()
    
    for reserva in reservas_cancha:
        reserva.hora_fin = reserva.hora_fin()
    
    return render(request, "crear_reserva.html", {
        "form": form,
        "cancha": cancha,
        "reservas_cancha": reservas_cancha,
    })


def conflicto_hora(reserva):
    
    inicio = datetime.combine(reserva.fecha, reserva.hora_inicio)
    fin = inicio + timedelta(minutes=reserva.duracion_bloques * 30)
    
    conflictos = Reserva.objects.filter(
        cancha=reserva.cancha,
        fecha=reserva.fecha,
        estado__in=["PENDIENTE", "CONFIRMADA"]).exclude(id=reserva.id)
    
    for x in conflictos:
        x_fin = datetime.combine(x.fecha, x.hora_fin())
        if not (fin.time() <= x.hora_inicio or reserva.hora_inicio >= x_fin.time()):
            return True
    return False


@login_required(login_url="cuentas:login_cuenta")
def listar_reservas(request):

    try:
        dueno = Dueno.objects.get(usuario=request.user)
        es_dueno = True
    except Dueno.DoesNotExist:
        es_dueno = False
    
    if es_dueno:

        canchas_propias = Cancha.objects.filter(
            establecimiento__dueno=dueno
        ).values_list("id", flat=True)
        
        reservas = Reserva.objects.filter(
            Q(usuario=request.user) | Q(cancha_id__in=canchas_propias)
        ).select_related("usuario", "cancha", "cancha__establecimiento").order_by("-fecha", "-hora_inicio")
    else:

        reservas = Reserva.objects.filter(
            usuario=request.user
        ).select_related("cancha", "cancha__establecimiento").order_by("-fecha", "-hora_inicio")
    
    return render(request, "listar_reservas.html", {
        "reservas": reservas,
        "es_dueno": es_dueno,
    })


@login_required(login_url='cuentas:login_cuenta')
def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    es_propietario = reserva.usuario == request.user
    es_dueno_cancha = False
    
    try:
        dueno = Dueno.objects.get(usuario=request.user)
        es_dueno_cancha = reserva.cancha.establecimiento.dueno == dueno
    except Dueno.DoesNotExist:
        pass
    
    if not (es_propietario or es_dueno_cancha):
        return HttpResponseForbidden('No tienes permiso')
    
    if request.method == 'POST':
        form = CrearReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            
            # Si es dueño, actualizar estado
            if es_dueno_cancha and 'estado' in request.POST:
                reserva.estado = request.POST['estado']
                reserva.save()
            
            messages.success(request, 'Reserva actualizada')
            return redirect('reservas:listar_reservas')
    else:
        form = CrearReservaForm(instance=reserva)
    
    return render(request, 'editar_reserva.html', {
        'form': form,
        'reserva': reserva,
        'es_dueno_cancha': es_dueno_cancha,
    })

@login_required(login_url="cuentas:login_cuenta")
@require_http_methods(["GET", "POST"])
def eliminar_reserva(request, reserva_id):
    
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    es_propietario = reserva.usuario == request.user
    es_dueno_cancha = False
    
    try:
        dueno = Dueno.objects.get(usuario=request.user)
        es_dueno_cancha = reserva.cancha.establecimiento.dueno == dueno
    except Dueno.DoesNotExist:
        pass
    
    if not (es_propietario or es_dueno_cancha):
        return HttpResponseForbidden("Solamente el dueno del establecimiento o reserva puede editarla")
    
    if request.method == "POST":
        fecha = reserva.fecha
        hora = reserva.hora_inicio
        reserva.delete()
        messages.success(request, "Reserva eliminada")
        return redirect("reservas:listar_reservas")
    
    return render(request, "eliminar_reserva.html", {
        "reserva": reserva,
    })
