from django.contrib import admin
from .models import (
    Categoria, Marca, Producto, Cliente, Proveedor, Perfil,
    Venta, DetalleVenta, Compra, DetalleCompra
)


class BaseAdmin(admin.ModelAdmin):
    readonly_fields = ("user", "fecha_creacion", "fecha_modificacion")

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)


admin.site.register([Categoria, Marca, Cliente, Proveedor, Perfil], BaseAdmin)


@admin.register(Producto)
class ProductoAdmin(BaseAdmin):
    list_display = ("nombre", "marca", "precio", "stock", "activo")
    search_fields = ("nombre",)
    list_filter = ("marca", "categorias", "activo")
    filter_horizontal = ("categorias",)


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1


@admin.register(Venta)
class VentaAdmin(BaseAdmin):
    list_display = ("id", "cliente", "fecha_hora", "tipo_pago", "total")
    list_filter = ("tipo_pago",)
    readonly_fields = BaseAdmin.readonly_fields + ("subtotal", "iva", "total")
    inlines = [DetalleVentaInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.calcular_totales()


class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1


@admin.register(Compra)
class CompraAdmin(BaseAdmin):
    list_display = ("id", "proveedor", "fecha_hora", "tipo_pago", "total")
    readonly_fields = BaseAdmin.readonly_fields + ("subtotal", "iva", "total")
    inlines = [DetalleCompraInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.calcular_totales()