from django.shortcuts import render, redirect, get_object_or_404
from establecimientos.models import Cancha, Establecimiento
from .models import Reserva
from cuentas.models import Usuario,Dueno
from .forms import CrearReservaForm
from django.contrib import messages
from datetime import datetime, timedelta
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
# Create your views here.


@login_required(login_url='cuentas:login_cuenta')
@require_http_methods(["GET", "POST"])
def crear_reserva(request, cancha_id):
    cancha = get_object_or_404(Cancha, id=cancha_id)
    
    reservas_cancha = Reserva.objects.filter(
        cancha=cancha,
        estado__in=['PENDIENTE', 'CONFIRMADA']
    ).select_related('usuario').order_by('fecha', 'hora_inicio')
    
    if request.method == 'POST':
        form = CrearReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.cancha = cancha
            reserva.usuario = request.user
            
            if conflicto_hora(reserva):
                messages.error(request, 'Ya existe una reserva en ese horario.')
            else:
                reserva.save()
                messages.success(request, 'Reserva creada exitosamente!')
                return redirect('cuentas:home')
                #return redirect('reservas:ver_reserva', id=reserva.id)
    else:
        form = CrearReservaForm()
    
    for reserva in reservas_cancha:
        reserva.hora_fin = reserva.hora_fin()
    
    return render(request, 'crear_reserva.html', {
        'form': form,
        'cancha': cancha,
        'reservas_cancha': reservas_cancha,
    })


def conflicto_hora(reserva):
    
    inicio = datetime.combine(reserva.fecha, reserva.hora_inicio)
    fin = inicio + timedelta(minutes=reserva.duracion_bloques * 30)
    
    conflictos = Reserva.objects.filter(
        cancha=reserva.cancha,
        fecha=reserva.fecha,
        estado__in=['PENDIENTE', 'CONFIRMADA']).exclude(id=reserva.id)
    
    for x in conflictos:
        x_fin = datetime.combine(x.fecha, x.hora_fin())
        if not (fin.time() <= x.hora_inicio or reserva.hora_inicio >= x_fin.time()):
            return True
    return False
