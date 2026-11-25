from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import ProtectedError, Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView

from .forms import (
    MarcaForm, CategoriaForm, ProductoForm, ClienteForm, ProveedorForm, PerfilForm,
    VentaForm, DetalleVentaFormSet, CompraForm, DetalleCompraFormSet
)
from .mixins import UsuarioRegistroMixin
from .models import (
    Marca, Categoria, Producto, Cliente, Proveedor, Perfil,
    Venta, Compra, TipoPago, IVA_TARIFA
)


# =====================================================================
# MARCAS · Vistas Basadas en Clases (VBC)
# =====================================================================
class MarcaListView(LoginRequiredMixin, ListView):
    model = Marca
    template_name = "facturacion/marca_lista.html"
    context_object_name = "marcas"
    paginate_by = 5
    extra_context = {"titulo": "Marcas"}

    def get_queryset(self):
        marcas = super().get_queryset()
        q = self.request.GET.get("q", "")
        if q:
            marcas = marcas.filter(nombre__icontains=q)
        return marcas

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["q"] = self.request.GET.get("q", "")
        return contexto


class MarcaCreateView(LoginRequiredMixin, UsuarioRegistroMixin, SuccessMessageMixin, CreateView):
    model = Marca
    form_class = MarcaForm
    template_name = "facturacion/marca_form.html"
    success_url = reverse_lazy("facturacion:marca_lista")
    success_message = "Marca «%(nombre)s» creada correctamente."
    extra_context = {"titulo": "Nueva marca", "boton": "Guardar"}


class MarcaUpdateView(LoginRequiredMixin, UsuarioRegistroMixin, SuccessMessageMixin, UpdateView):
    model = Marca
    form_class = MarcaForm
    template_name = "facturacion/marca_form.html"
    success_url = reverse_lazy("facturacion:marca_lista")
    success_message = "Marca «%(nombre)s» actualizada."
    extra_context = {"titulo": "Editar marca", "boton": "Actualizar"}

    def form_invalid(self, form):
        messages.error(self.request, "Revisa los campos marcados en rojo.")
        return super().form_invalid(form)


class MarcaDeleteView(LoginRequiredMixin, DeleteView):
    model = Marca
    template_name = "facturacion/marca_eliminar.html"
    context_object_name = "marca"
    success_url = reverse_lazy("facturacion:marca_lista")
    extra_context = {"titulo": "Eliminar marca"}

    def form_valid(self, form):
        nombre = self.object.nombre
        try:
            respuesta = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, f"No se puede eliminar «{nombre}»: tiene productos, desactívala.")
            return redirect("facturacion:marca_lista")
        messages.success(self.request, f"Marca «{nombre}» eliminada.")
        return respuesta


# =====================================================================
# CATEGORÍAS · Vistas Basadas en Clases (VBC)
# =====================================================================
class CategoriaListView(LoginRequiredMixin, ListView):
    model = Categoria
    template_name = "facturacion/categoria_lista.html"
    context_object_name = "categorias"
    paginate_by = 5
    extra_context = {"titulo": "Categorías"}

    def get_queryset(self):
        categorias = super().get_queryset()
        q = self.request.GET.get("q", "")
        if q:
            categorias = categorias.filter(nombre__icontains=q)
        return categorias

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["q"] = self.request.GET.get("q", "")
        return contexto


class CategoriaCreateView(LoginRequiredMixin, UsuarioRegistroMixin, SuccessMessageMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "facturacion/categoria_form.html"
    success_url = reverse_lazy("facturacion:categoria_lista")
    success_message = "Categoría «%(nombre)s» creada."
    extra_context = {"titulo": "Nueva categoría", "boton": "Guardar"}


class CategoriaUpdateView(LoginRequiredMixin, UsuarioRegistroMixin, SuccessMessageMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "facturacion/categoria_form.html"
    success_url = reverse_lazy("facturacion:categoria_lista")
    success_message = "Categoría «%(nombre)s» actualizada."
    extra_context = {"titulo": "Editar categoría", "boton": "Actualizar"}

    def form_invalid(self, form):
        messages.error(self.request, "Revisa los campos marcados en rojo.")
        return super().form_invalid(form)


class CategoriaDeleteView(LoginRequiredMixin, DeleteView):
    model = Categoria
    template_name = "facturacion/categoria_eliminar.html"
    context_object_name = "categoria"
    success_url = reverse_lazy("facturacion:categoria_lista")
    extra_context = {"titulo": "Eliminar categoría"}

    def form_valid(self, form):
        nombre = self.object.nombre
        respuesta = super().form_valid(form)
        messages.success(self.request, f"Categoría «{nombre}» eliminada.")
        return respuesta


# =====================================================================
# PRODUCTOS · Vistas Basadas en Clases (VBC)
# =====================================================================
class ProductoListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = "facturacion/producto_lista.html"
    context_object_name = "productos"
    paginate_by = 5
    extra_context = {"titulo": "Productos"}

    def get_queryset(self):
        productos = super().get_queryset()
        productos = productos.select_related("marca").prefetch_related("categorias")
        q = self.request.GET.get("q", "")
        if q:
            productos = productos.filter(nombre__icontains=q)
        return productos

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["q"] = self.request.GET.get("q", "")
        return contexto


class ProductoCreateView(LoginRequiredMixin, UsuarioRegistroMixin, SuccessMessageMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "facturacion/producto_form.html"
    success_url = reverse_lazy("facturacion:producto_lista")
    success_message = "Producto «%(nombre)s» creado."
    extra_context = {"titulo": "Nuevo producto", "boton": "Guardar"}


class ProductoUpdateView(LoginRequiredMixin, UsuarioRegistroMixin, SuccessMessageMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "facturacion/producto_form.html"
    success_url = reverse_lazy("facturacion:producto_lista")
    success_message = "Producto «%(nombre)s» actualizado."
    extra_context = {"titulo": "Editar producto", "boton": "Actualizar"}

    def form_invalid(self, form):
        messages.error(self.request, "Revisa los campos marcados en rojo.")
        return super().form_invalid(form)


class ProductoDetailView(LoginRequiredMixin, DetailView):
    model = Producto
    template_name = "facturacion/producto_detalle.html"
    context_object_name = "producto"


class ProductoDeleteView(LoginRequiredMixin, DeleteView):
    model = Producto
    template_name = "facturacion/producto_eliminar.html"
    context_object_name = "producto"
    success_url = reverse_lazy("facturacion:producto_lista")
    extra_context = {"titulo": "Eliminar producto"}

    def form_valid(self, form):
        nombre = self.object.nombre
        try:
            respuesta = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, f"No se puede eliminar «{nombre}»: ya tiene ventas o compras registradas.")
            return redirect("facturacion:producto_lista")
        messages.success(self.request, f"Producto «{nombre}» eliminado.")
        return respuesta


# =====================================================================
# CLIENTES · Vistas Basadas en Clases (VBC)
# =====================================================================
class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = "facturacion/cliente_lista.html"
    context_object_name = "clientes"
    paginate_by = 5
    extra_context = {"titulo": "Clientes"}

    def get_queryset(self):
        clientes = super().get_queryset()
        q = self.request.GET.get("q", "")
        if q:
            clientes = clientes.filter(Q(apellidos__icontains=q) | Q(cedula__icontains=q))
        return clientes

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["q"] = self.request.GET.get("q", "")
        return contexto


class ClienteCreateView(LoginRequiredMixin, UsuarioRegistroMixin, SuccessMessageMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "facturacion/cliente_form.html"
    success_url = reverse_lazy("facturacion:cliente_lista")
    success_message = "Cliente «%(apellidos)s %(nombres)s» creado."
    extra_context = {"titulo": "Nuevo cliente", "boton": "Guardar"}


class ClienteUpdateView(LoginRequiredMixin, UsuarioRegistroMixin, SuccessMessageMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "facturacion/cliente_form.html"
    success_url = reverse_lazy("facturacion:cliente_lista")
    success_message = "Cliente «%(apellidos)s %(nombres)s» actualizado."
    extra_context = {"titulo": "Editar cliente", "boton": "Actualizar"}

    def form_invalid(self, form):
        messages.error(self.request, "Revisa los campos marcados en rojo.")
        return super().form_invalid(form)


class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente
    template_name = "facturacion/cliente_detalle.html"
    context_object_name = "cliente"


class ClienteDeleteView(LoginRequiredMixin, DeleteView):
    model = Cliente
    template_name = "facturacion/cliente_eliminar.html"
    context_object_name = "cliente"
    success_url = reverse_lazy("facturacion:cliente_lista")
    extra_context = {"titulo": "Eliminar cliente"}

    def form_valid(self, form):
        nombre = str(self.object)
        try:
            respuesta = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, f"No se puede eliminar a «{nombre}»: ya tiene ventas registradas.")
            return redirect("facturacion:cliente_lista")
        messages.success(self.request, f"Cliente «{nombre}» eliminado.")
        return respuesta


# =====================================================================
# PROVEEDORES · Vistas Basadas en Clases (VBC)
# =====================================================================
class ProveedorListView(LoginRequiredMixin, ListView):
    model = Proveedor
    template_name = "facturacion/proveedor_lista.html"
    context_object_name = "proveedores"
    paginate_by = 5
    extra_context = {"titulo": "Proveedores"}

    def get_queryset(self):
        proveedores = super().get_queryset()
        q = self.request.GET.get("q", "")
        if q:
            proveedores = proveedores.filter(
                Q(nombre__icontains=q) | Q(apellido__icontains=q) | Q(ruc__icontains=q)
            )
        return proveedores

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["q"] = self.request.GET.get("q", "")
        return contexto


class ProveedorCreateView(LoginRequiredMixin, UsuarioRegistroMixin, SuccessMessageMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = "facturacion/proveedor_form.html"
    success_url = reverse_lazy("facturacion:proveedor_lista")
    success_message = "Proveedor «%(nombre)s %(apellido)s» creado."
    extra_context = {"titulo": "Nuevo proveedor", "boton": "Guardar"}


class ProveedorUpdateView(LoginRequiredMixin, UsuarioRegistroMixin, SuccessMessageMixin, UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = "facturacion/proveedor_form.html"
    success_url = reverse_lazy("facturacion:proveedor_lista")
    success_message = "Proveedor «%(nombre)s %(apellido)s» actualizado."
    extra_context = {"titulo": "Editar proveedor", "boton": "Actualizar"}

    def form_invalid(self, form):
        messages.error(self.request, "Revisa los campos marcados en rojo.")
        return super().form_invalid(form)


class ProveedorDetailView(LoginRequiredMixin, DetailView):
    model = Proveedor
    template_name = "facturacion/proveedor_detalle.html"
    context_object_name = "proveedor"


class ProveedorDeleteView(LoginRequiredMixin, DeleteView):
    model = Proveedor
    template_name = "facturacion/proveedor_eliminar.html"
    context_object_name = "proveedor"
    success_url = reverse_lazy("facturacion:proveedor_lista")
    extra_context = {"titulo": "Eliminar proveedor"}

    def form_valid(self, form):
        nombre = str(self.object)
        try:
            respuesta = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, f"No se puede eliminar a «{nombre}»: tiene compras registradas.")
            return redirect("facturacion:proveedor_lista")
        messages.success(self.request, f"Proveedor «{nombre}» eliminado.")
        return respuesta


# =====================================================================
# VENTAS (maestro-detalle) · Vistas Basadas en Clases
# =====================================================================
class VentaListView(LoginRequiredMixin, ListView):
    model = Venta
    template_name = "facturacion/venta_lista.html"
    context_object_name = "ventas"
    paginate_by = 10
    extra_context = {"titulo": "Ventas", "tipos_pago": TipoPago.choices}

    def get_queryset(self):
        ventas = super().get_queryset().select_related("cliente")
        q = self.request.GET.get("q", "")
        tipo = self.request.GET.get("tipo_pago", "")
        if q:
            ventas = ventas.filter(
                Q(cliente__apellidos__icontains=q) | Q(cliente__cedula__icontains=q)
            )
        if tipo:
            ventas = ventas.filter(tipo_pago=tipo)
        return ventas

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["q"] = self.request.GET.get("q", "")
        contexto["tipo_pago"] = self.request.GET.get("tipo_pago", "")
        return contexto


class VentaDetallesMixin:
    model = Venta
    form_class = VentaForm
    template_name = "facturacion/venta_form.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        if "detalles" not in contexto:
            contexto["detalles"] = DetalleVentaFormSet(instance=self.object)
        return contexto

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        detalles = DetalleVentaFormSet(request.POST, instance=self.object)
        if form.is_valid() and detalles.is_valid():
            return self.form_valid(form, detalles)
        return self.form_invalid(form, detalles)

    def form_valid(self, form, detalles):
        with transaction.atomic():
            if self.object:
                self.object.devolver_stock()
            form.instance.user = self.request.user
            self.object = form.save()
            self.guardar_detalles(detalles)
            self.object.descontar_stock()
            self.object.calcular_totales()
        messages.success(self.request, f"{self.object} guardada. Total: ${self.object.total}")
        return HttpResponseRedirect(self.get_success_url())

    def guardar_detalles(self, detalles):
        detalles.instance = self.object
        filas = detalles.save(commit=False)
        for fila in detalles.deleted_objects:
            fila.delete()
        cambio_producto = {obj.pk for obj, campos in detalles.changed_objects if "producto" in campos}
        for fila in filas:
            if fila.pk is None or fila.pk in cambio_producto:
                fila.precio = fila.producto.precio
            fila.user = self.request.user
            fila.save()

    def form_invalid(self, form, detalles):
        messages.error(self.request, "Revisa los datos de la venta.")
        return self.render_to_response(self.get_context_data(form=form, detalles=detalles))

    def get_success_url(self):
        return reverse("facturacion:venta_detalle", kwargs={"pk": self.object.pk})


class VentaCreateView(LoginRequiredMixin, VentaDetallesMixin, CreateView):
    extra_context = {"titulo": "Nueva venta", "boton": "Guardar venta"}

    def post(self, request, *args, **kwargs):
        self.object = None
        return super().post(request, *args, **kwargs)


class VentaUpdateView(LoginRequiredMixin, VentaDetallesMixin, UpdateView):
    extra_context = {"titulo": "Editar venta", "boton": "Actualizar venta"}

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class VentaDetailView(LoginRequiredMixin, DetailView):
    model = Venta
    template_name = "facturacion/venta_detalle.html"
    context_object_name = "venta"

    def get_queryset(self):
        return super().get_queryset().select_related("cliente", "user").prefetch_related("detalles__producto")

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["iva_porcentaje"] = IVA_TARIFA * 100
        return contexto


class VentaDeleteView(LoginRequiredMixin, DeleteView):
    model = Venta
    template_name = "facturacion/venta_eliminar.html"
    context_object_name = "venta"
    success_url = reverse_lazy("facturacion:venta_lista")

    def form_valid(self, form):
        with transaction.atomic():
            self.object.devolver_stock()
            respuesta = super().form_valid(form)
        messages.success(self.request, "Venta eliminada y stock devuelto.")
        return respuesta


# =====================================================================
# COMPRAS (maestro-detalle) · Vistas Basadas en Clases
# =====================================================================
class CompraListView(LoginRequiredMixin, ListView):
    model = Compra
    template_name = "facturacion/compra_lista.html"
    context_object_name = "compras"
    paginate_by = 10
    extra_context = {"titulo": "Compras", "tipos_pago": TipoPago.choices}

    def get_queryset(self):
        compras = super().get_queryset().select_related("proveedor")
        q = self.request.GET.get("q", "")
        tipo = self.request.GET.get("tipo_pago", "")
        if q:
            compras = compras.filter(
                Q(proveedor__nombre__icontains=q)
                | Q(proveedor__apellido__icontains=q)
                | Q(proveedor__ruc__icontains=q)
            )
        if tipo:
            compras = compras.filter(tipo_pago=tipo)
        return compras

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["q"] = self.request.GET.get("q", "")
        contexto["tipo_pago"] = self.request.GET.get("tipo_pago", "")
        return contexto


class CompraDetallesMixin:
    model = Compra
    form_class = CompraForm
    template_name = "facturacion/compra_form.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        if "detalles" not in contexto:
            contexto["detalles"] = DetalleCompraFormSet(instance=self.object)
        return contexto

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        detalles = DetalleCompraFormSet(request.POST, instance=self.object)
        if form.is_valid() and detalles.is_valid():
            return self.form_valid(form, detalles)
        return self.form_invalid(form, detalles)

    def form_valid(self, form, detalles):
        with transaction.atomic():
            if self.object:
                self.object.revertir_stock()
            form.instance.user = self.request.user
            self.object = form.save()
            self.guardar_detalles(detalles)
            self.object.ingresar_stock()
            self.object.calcular_totales()
        messages.success(self.request, f"{self.object} guardada. Total: ${self.object.total}")
        return HttpResponseRedirect(self.get_success_url())

    def guardar_detalles(self, detalles):
        detalles.instance = self.object
        filas = detalles.save(commit=False)
        for fila in detalles.deleted_objects:
            fila.delete()
        for fila in filas:
            fila.user = self.request.user
            fila.save()

    def form_invalid(self, form, detalles):
        messages.error(self.request, "Revisa los datos de la compra.")
        return self.render_to_response(self.get_context_data(form=form, detalles=detalles))

    def get_success_url(self):
        return reverse("facturacion:compra_detalle", kwargs={"pk": self.object.pk})


class CompraCreateView(LoginRequiredMixin, CompraDetallesMixin, CreateView):
    extra_context = {"titulo": "Nueva compra", "boton": "Guardar compra"}

    def post(self, request, *args, **kwargs):
        self.object = None
        return super().post(request, *args, **kwargs)


class CompraUpdateView(LoginRequiredMixin, CompraDetallesMixin, UpdateView):
    extra_context = {"titulo": "Editar compra", "boton": "Actualizar compra"}

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class CompraDetailView(LoginRequiredMixin, DetailView):
    model = Compra
    template_name = "facturacion/compra_detalle.html"
    context_object_name = "compra"

    def get_queryset(self):
        return super().get_queryset().select_related("proveedor", "user").prefetch_related("detalles__producto")

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["iva_porcentaje"] = IVA_TARIFA * 100
        return contexto


class CompraDeleteView(LoginRequiredMixin, DeleteView):
    model = Compra
    template_name = "facturacion/compra_eliminar.html"
    context_object_name = "compra"
    success_url = reverse_lazy("facturacion:compra_lista")

    def form_valid(self, form):
        with transaction.atomic():
            self.object.revertir_stock()
            respuesta = super().form_valid(form)
        messages.success(self.request, "Compra eliminada y stock revertido.")
        return respuesta


# =====================================================================
# MI PERFIL (Reto con UpdateView sin pk en la URL)
# =====================================================================
class MiPerfilView(LoginRequiredMixin, UsuarioRegistroMixin, SuccessMessageMixin, UpdateView):
    model = Perfil
    form_class = PerfilForm
    template_name = "facturacion/perfil_form.html"
    success_url = reverse_lazy("facturacion:mi_perfil")
    success_message = "Tu perfil se ha actualizado correctamente."
    extra_context = {"titulo": "Mi Perfil", "boton": "Guardar cambios"}

    def get_object(self, queryset=None):
        perfil, creado = Perfil.objects.get_or_create(usuario=self.request.user)
        return perfil