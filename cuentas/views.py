from django.shortcuts import render
from .forms import RegistroForm
from django.template import loader
from django.http import HttpResponse
from .models import Usuario,Cliente,Dueno
from django.contrib import messages
from django.contrib.auth import authenticate
from django.db import transaction

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
                
                
            else:                        
                Cliente.objects.create(usuario=usuario)
                #c.save()

            """   
            try:
                with transaction.atomic():

                    usuario = form.save()
                    tipo_usuario = form.cleaned_data["tipo_usuario"]

                    if tipo_usuario == "dueno":
                        
                        Dueno.objects.create(
                            usuario=usuario,
                            rut=form.cleaned_data["rut"]
                        )
                        

                        d = Dueno(usuario = usuario, rut = form.cleaned_data["rut"])
                        d.save()
                        
                        
                    else:
                        
                        Cliente.objects.create(
                            usuario=usuario,               
                        )
                        
                        c = Cliente(usuario=usuario)
                        c.save()

                        

                    messages.success(request, f"Cuenta creada exitosamente, Bienvenido {usuario.username}!")
            except Exception as e :
                messages.error(request, f"Hubo un errror {str(e)} ")
            """

    else:
        form = RegistroForm()

    context = {
        "form" : form
    }

    return HttpResponse(template.render(context,request))
    #return render (request, "registro.html", {"form":form})

def login(request):


    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        usuario = authenticate(request, username=username, password=password)

        if usuario is not None:
            login(request, usuario)
            messages.success(request, f"Sesión iniciada correctamente, Bienvenido {usuario.username}")
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render (request, "login.html")