from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from cuentas.models import Dueno
from django.contrib import messages
from .forms import CrearEstablecimientoForm


# Create your views here.

def buscar(request):
    return render (request,"buscar.html")

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
        else:
            messages.error(request, "Formulario invalido")

    else:
        form = CrearEstablecimientoForm()

    context = {
        "form" : form,

    }


    return render (request,"crear_establecimiento.html",context)