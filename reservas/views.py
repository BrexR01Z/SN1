from django.shortcuts import render, redirect, get_object_or_404
from establecimientos.models import Cancha, Establecimiento
from .models import Reserva
from cuentas.models import Usuario,Dueno
from .forms import CrearReservaForm
from django.contrib import messages
from datetime import datetime, timedelta
# Create your views here.


def crear_reserva(request, cancha_id):
    cancha = get_object_or_404(Cancha, id=cancha_id)

    if request.method == "POST" : 
        form = CrearReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.cancha = cancha
            reserva.usuario = request.user

            if revisar_horario(reserva):
                messages.error(request, "Ya existe una reserva en ese horario")
            else:                
                reserva.save()
                messages.success(request,"Reserva creada exitosamente")
                return redirect ("cuentas:home")
            # sugerir mandar invitaciones luego de hacer reserva exitosa
                # return redirect("MOSTRAR DETALLE RESERVA, HACER", id=reserva.id)
    else:
        form = CrearReservaForm()

    context = {
        "form" : form,
        "cancha" : cancha,
    }

    return render (request, "crear_reserva.html", context)


def revisar_horario(reserva):
    inicio = datetime.combine(reserva.fecha, reserva.hora_inicio)
    fin = inicio + timedelta(minutes=reserva.duracion_bloques * 30)

    conflictos = Reserva.objects.filter(
        cancha=reserva.cancha,
        fecha=reserva.fecha,
        estado__in=['PENDIENTE', 'CONFIRMADA']
    ).exclude(id=reserva.id)
    
    for x in conflictos:
        x_fin = datetime.combine(x.fecha, x.hora_fin())
        if not (fin.time() <= x.hora_inicio or reserva.hora_inicio >= x_fin.time()):
            return True
    return False

