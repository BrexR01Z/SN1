from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.http import HttpResponse, HttpResponseForbidden
from cuentas.models import Dueno
from .models import Establecimiento, Cancha, HorarioEstablecimiento
from django.contrib import messages
from .forms import CrearEstablecimientoForm, CrearCanchaForm, HorarioEstablecimientoForm, HorarioFormSet
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


# Create your views here.

# ----------------- ESTABLECIMIENTO

def crear_establecimiento(request):

    try: 
        dueno = Dueno.objects.get(usuario=request.user)

    except Dueno.DoesNotExist: 
        messages.error(request, "Solo los usuarios dueno pueden ingresar")
        return redirect ("cuentas:home")

    if request.method == "POST":
        form = CrearEstablecimientoForm(request.POST)
        formset = HorarioFormSet(request.POST, instance = None)

        if form.is_valid():
            establecimiento = form.save(commit=False)
            establecimiento.dueno = dueno

            if formset.is_valid():
                establecimiento.save()

                for horario_form in formset:
                    if horario_form.cleaned_data and not horario_form.cleaned_data.get("DELETE"):
                        horario = horario_form.save(commit=False)
                        horario.establecimiento = establecimiento
                        horario.save()

                messages.success(request, "Establecimiento y horarios creado")

                # return redirect ("establecimientos:ver_establecimiento", id= establecimiento.id)
                return redirect ("establecimientos:ver_establecimiento", establecimiento= establecimiento.id)
                    
            else:
                messages.error(request, "Corriga los errores del formulario.")
                establecimiento.delete()

            # messages.success(request, "Establecimiento creado")

            # return redirect ("cuentas:SportsNet_dueno")
        else:
            messages.error(request, "Corriga los errores del formulario.")

    else:
        form = CrearEstablecimientoForm()
        formset = HorarioFormSet(instance=None, queryset=HorarioEstablecimiento.objects.none())

    context = {
        "form" : form,
        "formset" : formset,

    }


    return render (request,"crear_establecimiento.html",context)


def ver_establecimiento(request, establecimiento):
       
    # establecimiento = get_object_or_404(Establecimiento, pk=establecimiento)
    establecimiento = Establecimiento.objects.get(id=establecimiento)
    context = {
        'establecimiento': establecimiento,        
    }

    return render(request, 'ver_establecimiento.html', context)

@login_required(login_url='cuentas:login_cuenta')
def editar_establecimiento(request, establecimiento_id):

    establecimiento = get_object_or_404(Establecimiento, id = establecimiento_id)

    try:
        dueno = Dueno.objects.get(usuario=request.user)
    except Dueno.DoesNotExist:
        return HttpResponseForbidden("Solo los usuarios dueno pueden acceder")

    if establecimiento.dueno != dueno:
        return HttpResponseForbidden("Solo los respectivos duenos tienen acceso a sus establecimientos")
    
    if request.method == "POST":
        form = CrearEstablecimientoForm(request.POST, instance=establecimiento)
        
        if form.is_valid():
            form.save()
            messages.success(request, f"Establecimiento actualizado exitosamente")
            return redirect ("establecimientos:ver_establecimiento", establecimiento = establecimiento.id)
    else:
        form= CrearEstablecimientoForm(instance=establecimiento)

    context = {
        "form":form,
        "establecimiento":establecimiento,
    }

    return render (request, "editar_establecimiento.html", context)

@login_required(login_url='cuentas:login_cuenta')
@require_http_methods(["GET", "POST"])
def eliminar_establecimiento(request, establecimiento_id):
    
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    
    try:
        dueno = Dueno.objects.get(usuario=request.user)
    except Dueno.DoesNotExist:
        return HttpResponseForbidden("Solo los usuarios dueno pueden acceder a esta funcion")
    
    if establecimiento.dueno != dueno:
        return HttpResponseForbidden("Solo los respectivos duenos pueden eliminar sus establecimientos")
    
    if request.method == 'POST':
        nombre = establecimiento.nombre
        establecimiento.delete()
        messages.success(request, f'Establecimiento eliminado correctamente')
        return redirect('cuentas:SportsNet_dueno')
    
    context = {
        "establecimiento" : establecimiento,
    }
    
    return render(request, 'eliminar_establecimiento.html',context)


# ----------------------- CANCHA -----------------------------------

@login_required(login_url='cuentas:login_cuenta')
@require_http_methods(["GET", "POST"])
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

def ver_cancha(request, cancha_id):
    cancha = get_object_or_404(Cancha, id=cancha_id)
    est = cancha.establecimiento

    horarios = HorarioEstablecimiento.objects.filter(establecimiento=est).order_by("dia")

    dias_semana = ["Lunes","Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
    horarios_est = {}

    for x in dias_semana:
        horarios_est[x] = None

    for x in horarios:
        horarios_est[x.dia] = x

    context = {
        "cancha" : cancha,
        "horarios" : horarios,
        # "horarios_est" : horarios_est,
    }

    return render(request, "ver_cancha.html",context)


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