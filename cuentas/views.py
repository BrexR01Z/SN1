from django.shortcuts import render, redirect
from .forms import RegistroForm
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from .models import Usuario,Cliente,Dueno
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.urls import reverse

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

            return redirect("cuentas:home")

    else:
        form = RegistroForm()

    context = {
        "form" : form
    }

    return HttpResponse(template.render(context,request))
    #return HttpResponseRedirect(reverse("cuentas:home"))
    #return render (request, "registro.html", {"form":form})

def login_cuenta(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        

        if user is not None:
            
            login(request, user)
            
            messages.success(request, f"Sesión iniciada correctamente, Bienvenido {user.username}")
            return redirect("cuentas:home")
            
            # redirect a dashboard segun tipo_cuenta
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
            
    """
    context = {
        "user":user,
    }
    """

    return render (request, "login.html")

def home (request):
    return render(request,"home.html")

@login_required
def cerrar_sesion(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente')
    return redirect("cuentas:home")
