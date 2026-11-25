from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from facturacion.models import Producto, Venta


class InicioView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        hoy = timezone.localdate()
        ventas_hoy = Venta.objects.filter(fecha_hora__date=hoy)
        contexto["total_productos"] = Producto.objects.filter(activo=True).count()
        contexto["ventas_hoy"] = ventas_hoy.count()
        contexto["vendido_hoy"] = ventas_hoy.aggregate(suma=Sum("total"))["suma"] or 0
        contexto["stock_bajo"] = Producto.objects.filter(activo=True, stock__lt=5)
        return contexto


def ingresar(request):
    if request.user.is_authenticated:
        return redirect("home")
    siguiente = request.POST.get("next") or request.GET.get("next") or ""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if siguiente and url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
                return redirect(siguiente)
            return redirect("home")
    else:
        form = AuthenticationForm(request)
    return render(request, "registration/login.html", {"form": form, "next": siguiente})


@require_POST
def salir(request):
    logout(request)
    messages.info(request, "Cerraste sesión.")
    return redirect("login")


def registro(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, f"¡Bienvenido, {usuario.username}!")
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "registration/registro.html", {"form": form})