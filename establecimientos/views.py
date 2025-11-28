from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.http import HttpResponse, HttpResponseForbidden
from cuentas.models import Dueno
from .models import Establecimiento, Cancha
from django.contrib import messages
from .forms import CrearEstablecimientoForm, CrearCanchaForm


# Create your views here.

def buscar(request):
    
    DEPORTES = ["FUTBOL",
                "BASQUETBALL",
                "VOLEYBALL", 
                "TENIS", 
                "RUGBY", 
                "HANDBALL", 
                "BOWLING", 
                "SQUASH", 
                "PADEL", 
                "OTRO"
                ]
        

    canchas = Cancha.objects.all
    #deportes = Deporte.objects.all

    context = {
        "canchas" : canchas,
        "deportes" : DEPORTES,
        #"deportes" : deportes,
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


#@login_required(login_url='cuentas:login_cuenta')
#@require_http_methods(["GET", "POST"])
def crear_cancha(request, establecimiento_id):

    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    
    try:
        dueno = Dueno.objects.get(usuario=request.user)
    except Dueno.DoesNotExist:
        return HttpResponseForbidden('Solo los dueños pueden crear canchas.')
    
    if establecimiento.dueno != dueno:
        return HttpResponseForbidden('Solo el dueño del establecimiento puede hacer canchas para los respectivos establecimientos')
    
    if request.method == 'POST':
        form = CrearCanchaForm(request.POST)
        
        if form.is_valid():
            cancha = form.save(commit=False)
            cancha.establecimiento = establecimiento
            cancha.save()
            
            messages.success(request, f'Cancha creada exitosamente')

            return redirect('establecimientos:ver_establecimiento', establecimiento=establecimiento.id)
        
        else:
            messages.error(request, 'Revisa los errores del formulario')
    
    else:
        form = CrearCanchaForm()
    
    context = {
        'form': form,
        'establecimiento': establecimiento,
        'establecimiento_id': establecimiento.id,
    }
    
    return render(request, 'crear_cancha.html', context)