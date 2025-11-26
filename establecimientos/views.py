from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.http import HttpResponse
from cuentas.models import Dueno
from .models import Establecimiento, Cancha, Deporte
from django.contrib import messages
from .forms import CrearEstablecimientoForm


# Create your views here.

def buscar(request):
    

    canchas = Cancha.objects.all
    deportes = Deporte.objects.all

    context = {
        "canchas" : canchas,
        "deportes" : deportes,
    }

    return render (request,"buscar.html", context)

def crear_establecimiento(request):

    try: 
        dueno = Dueno.objects.get(usuario=request.user)

    except Dueno.DoesNotExist: messages.error(request, "Solo los usuarios dueno pueden ingresar")

    if request.method == "POST":
        form = CrearEstablecimientoForm(request.POST)

        if form.is_valid():
            establecimiento = form.save(commit=False)
            establecimiento.dueno = dueno
            establecimiento.save()

            messages.success(request, "Establecimiento creado")
            return redirect ("cuentas:SportsNet_dueno")
        else:
            messages.error(request, "Formulario invalido")

    else:
        form = CrearEstablecimientoForm()

    context = {
        "form" : form,

    }


    return render (request,"crear_establecimiento.html",context)


def ver_establecimiento(request, establecimiento):
       
    # establecimiento = get_object_or_404(Establecimiento, pk=establecimiento)
    establecimiento = Establecimiento.objects.get(id=establecimiento)
    context = {
        'establecimiento': establecimiento,        
    }

    return render(request, 'ver_establecimiento.html', context)
