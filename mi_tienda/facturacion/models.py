from decimal import Decimal
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F
from django.utils import timezone

IVA_TARIFA = Decimal("0.15")
DOS_DECIMALES = Decimal("0.01")


class ModeloBase(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name="%(class)s_registrados",
        verbose_name="Registrado por",
    )
    fecha_creacion = models.DateTimeField("Fecha de creación", auto_now_add=True)
    fecha_modificacion = models.DateTimeField("Última modificación", auto_now=True)

    class Meta:
        abstract = True


class TipoPago(models.TextChoices):
    CONTADO = "contado", "Contado"
    CREDITO = "credito", "Crédito"
    TRANSFERENCIA = "transferencia", "Transferencia"
    TARJETA = "tarjeta", "Tarjeta"


class Categoria(ModeloBase):
    nombre = models.CharField(max_length=60, unique=True)
    descripcion = models.TextField("Descripción", blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Marca(ModeloBase):
    nombre = models.CharField(max_length=60, unique=True)
    pais_origen = models.CharField("País de origen", max_length=60, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(ModeloBase):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField("Descripción", blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to="productos/", blank=True)
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name="productos")
    categorias = models.ManyToManyField(Categoria, related_name="productos", blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Cliente(ModeloBase):
    cedula = models.CharField("Cédula", max_length=10, unique=True)
    nombres = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=80)
    email = models.EmailField("Correo", blank=True)
    telefono = models.CharField("Teléfono", max_length=15, blank=True)
    direccion = models.CharField("Dirección", max_length=200, blank=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["apellidos", "nombres"]

    def __str__(self):
        return f"{self.apellidos} {self.nombres}"


class Proveedor(ModeloBase):
    nombre = models.CharField(max_length=80)
    apellido = models.CharField(max_length=80)
    ruc = models.CharField("RUC", max_length=13, unique=True)
    email = models.EmailField("Correo", blank=True)
    contacto = models.CharField("Teléfono de contacto", max_length=15, blank=True)
    logo = models.ImageField(upload_to="proveedores/", blank=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ["nombre", "apellido"]

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Perfil(ModeloBase):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    cedula = models.CharField("Cédula", max_length=10, blank=True)
    telefono = models.CharField("Teléfono", max_length=15, blank=True)
    cargo = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return f"Perfil de {self.usuario.username}"


class Venta(ModeloBase):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="ventas")
    fecha_hora = models.DateTimeField("Fecha y hora", default=timezone.now)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    iva = models.DecimalField("IVA", max_digits=12, decimal_places=2, default=0, editable=False)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    tipo_pago = models.CharField(
        "Tipo de pago",
        max_length=15,
        choices=TipoPago.choices,
        default=TipoPago.CONTADO,
    )

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ["-fecha_hora"]

    def __str__(self):
        return f"Venta #{self.pk}"

    def calcular_totales(self):
        subtotal = sum((d.subtotal for d in self.detalles.all()), Decimal("0"))
        self.subtotal = subtotal.quantize(DOS_DECIMALES)
        self.iva = (self.subtotal * IVA_TARIFA).quantize(DOS_DECIMALES)
        self.total = self.subtotal + self.iva
        self.save(update_fields=["subtotal", "iva", "total", "fecha_modificacion"])

    def descontar_stock(self):
        for detalle in self.detalles.all():
            Producto.objects.filter(pk=detalle.producto_id).update(stock=F("stock") - detalle.cantidad)

    def devolver_stock(self):
        for detalle in self.detalles.all():
            Producto.objects.filter(pk=detalle.producto_id).update(stock=F("stock") + detalle.cantidad)


class DetalleVenta(ModeloBase):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="detalles_venta")
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Detalle de venta"
        verbose_name_plural = "Detalles de venta"

    def __str__(self):
        return f"{self.cantidad} x {self.producto}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio


class Compra(ModeloBase):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name="compras")
    fecha_hora = models.DateTimeField("Fecha y hora", default=timezone.now)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    iva = models.DecimalField("IVA", max_digits=12, decimal_places=2, default=0, editable=False)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    tipo_pago = models.CharField(
        "Tipo de pago",
        max_length=15,
        choices=TipoPago.choices,
        default=TipoPago.CONTADO,
    )

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ["-fecha_hora"]

    def __str__(self):
        return f"Compra #{self.pk}"

    def calcular_totales(self):
        subtotal = sum((d.subtotal for d in self.detalles.all()), Decimal("0"))
        self.subtotal = subtotal.quantize(DOS_DECIMALES)
        self.iva = (self.subtotal * IVA_TARIFA).quantize(DOS_DECIMALES)
        self.total = self.subtotal + self.iva
        self.save(update_fields=["subtotal", "iva", "total", "fecha_modificacion"])

    def ingresar_stock(self):
        for detalle in self.detalles.all():
            Producto.objects.filter(pk=detalle.producto_id).update(stock=F("stock") + detalle.cantidad)

    def revertir_stock(self):
        for detalle in self.detalles.all():
            Producto.objects.filter(pk=detalle.producto_id).update(stock=F("stock") - detalle.cantidad)


class DetalleCompra(ModeloBase):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="detalles_compra")
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    precio = models.DecimalField("Costo unitario", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Detalle de compra"
        verbose_name_plural = "Detalles de compra"

    def __str__(self):
        return f"{self.cantidad} x {self.producto}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio