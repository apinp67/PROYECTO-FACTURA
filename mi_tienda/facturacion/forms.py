from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory
from .models import (
    Marca, Categoria, Producto, Cliente, Proveedor, Perfil,
    Venta, DetalleVenta, Compra, DetalleCompra
)


# =====================================================================
# CATÁLOGO: Marca, Categoría y Producto
# =====================================================================
class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ["nombre", "pais_origen", "activo"]
        labels = {"nombre": "Nombre de la marca"}
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Samsung"}),
            "pais_origen": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Corea del Sur"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 letras.")
        return nombre.title()


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Laptops"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if len(nombre) < 3:
            raise forms.ValidationError("El nombre debe tener al menos 3 letras.")
        return nombre.capitalize()


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["nombre", "descripcion", "marca", "categorias", "precio", "stock", "imagen", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Galaxy A55"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "marca": forms.Select(attrs={"class": "form-select"}),
            "categorias": forms.CheckboxSelectMultiple(),
            "precio": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["marca"].queryset = Marca.objects.filter(activo=True)
        self.fields["marca"].empty_label = "- Elige una marca -"

    def clean_precio(self):
        precio = self.cleaned_data["precio"]
        if precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor que 0.")
        return precio


# =====================================================================
# PERSONAS: Cliente, Proveedor y Perfil
# =====================================================================
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["cedula", "nombres", "apellidos", "email", "telefono", "direccion"]
        widgets = {
            "cedula": forms.TextInput(attrs={"class": "form-control", "placeholder": "10 dígitos"}),
            "nombres": forms.TextInput(attrs={"class": "form-control"}),
            "apellidos": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data["cedula"].strip()
        if not cedula.isdigit():
            raise forms.ValidationError("La cédula solo debe contener números.")
        if len(cedula) != 10:
            raise forms.ValidationError("La cédula debe tener exactamente 10 dígitos.")
        return cedula


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ["nombre", "apellido", "ruc", "email", "contacto", "logo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "apellido": forms.TextInput(attrs={"class": "form-control"}),
            "ruc": forms.TextInput(attrs={"class": "form-control", "placeholder": "13 dígitos terminados en 001"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "contacto": forms.TextInput(attrs={"class": "form-control"}),
            "logo": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }

    def clean_ruc(self):
        ruc = self.cleaned_data["ruc"].strip()
        if not ruc.isdigit():
            raise forms.ValidationError("El RUC solo debe contener números.")
        if len(ruc) != 13:
            raise forms.ValidationError("El RUC debe tener exactamente 13 dígitos.")
        if not ruc.endswith("001"):
            raise forms.ValidationError("El RUC debe terminar en 001.")
        return ruc


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ["cedula", "telefono", "cargo"]
        widgets = {
            "cedula": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "cargo": forms.TextInput(attrs={"class": "form-control"}),
        }


# =====================================================================
# VENTAS: Cabecera, Filas y Formset
# =====================================================================
class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ["cliente", "fecha_hora", "tipo_pago"]
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-select"}),
            "fecha_hora": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "tipo_pago": forms.Select(attrs={"class": "form-select"}),
        }


class ProductoConPrecioField(forms.ModelChoiceField):
    """Lista desplegable de productos que muestra también el precio y el stock."""
    def label_from_instance(self, obj):
        return f"{obj.nombre} · ${obj.precio} · stock: {obj.stock}"


class DetalleVentaForm(forms.ModelForm):
    producto = ProductoConPrecioField(
        queryset=Producto.objects.filter(activo=True),
        empty_label="- Elige un producto -",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = DetalleVenta
        fields = ["producto", "cantidad"]
        widgets = {
            "cantidad": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
        }


class BaseDetalleVentaFormSet(BaseInlineFormSet):
    """Validación de TODAS las filas juntas: ¿hay stock para lo que se pide?"""
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        pedido = {}
        for fila in self.forms:
            datos = fila.cleaned_data
            if not datos or datos.get("DELETE"):
                continue
            producto = datos["producto"]
            pedido[producto] = pedido.get(producto, 0) + datos["cantidad"]

        anterior = {}
        if self.instance.pk:
            for detalle in self.instance.detalles.all():
                anterior[detalle.producto_id] = anterior.get(detalle.producto_id, 0) + detalle.cantidad

        for producto, cantidad in pedido.items():
            disponible = producto.stock + anterior.get(producto.pk, 0)
            if cantidad > disponible:
                raise ValidationError(
                    f"Stock insuficiente de «{producto.nombre}»: pides {cantidad} y hay {disponible}."
                )


DetalleVentaFormSet = inlineformset_factory(
    Venta,
    DetalleVenta,
    form=DetalleVentaForm,
    formset=BaseDetalleVentaFormSet,
    extra=0,
    min_num=1,
    validate_min=True,
    can_delete=True,
)


# =====================================================================
# COMPRAS: Cabecera, Filas y Formset
# =====================================================================
class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ["proveedor", "fecha_hora", "tipo_pago"]
        widgets = {
            "proveedor": forms.Select(attrs={"class": "form-select"}),
            "fecha_hora": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "tipo_pago": forms.Select(attrs={"class": "form-select"}),
        }


class DetalleCompraForm(forms.ModelForm):
    producto = ProductoConPrecioField(
        queryset=Producto.objects.filter(activo=True),
        empty_label="- Elige un producto -",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = DetalleCompra
        fields = ["producto", "cantidad", "precio"]
        widgets = {
            "cantidad": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "precio": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0.01"}),
        }


DetalleCompraFormSet = inlineformset_factory(
    Compra,
    DetalleCompra,
    form=DetalleCompraForm,
    extra=0,
    min_num=1,
    validate_min=True,
    can_delete=True,
)