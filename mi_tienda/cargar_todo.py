import os
from io import BytesIO
from pathlib import Path
from decimal import Decimal
import django
from PIL import Image, ImageDraw

# 1. Configurar el entorno de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mi_tienda.settings")
django.setup()

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from facturacion.models import (
    Marca, Categoria, Producto, Cliente, Proveedor, Perfil,
    Venta, DetalleVenta, Compra, DetalleCompra, TipoPago
)

# =====================================================================
# PARTE 1: Asegurar las plantillas de Categoría (con conteo) y Cliente (con enlace a detalle)
# =====================================================================
base_app = Path("facturacion/templates/facturacion")
base_root = Path("templates/facturacion")
destino = base_app if base_app.exists() else base_root
destino.mkdir(parents=True, exist_ok=True)

plantillas_extra = {
    "categoria_lista.html": """{% extends "base.html" %}
{% block titulo %}{{ titulo }}{% endblock %}
{% block contenido %}
<div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
    <h1 class="h3 titulo-pagina m-0">{{ titulo }}</h1>
    <a href="{% url 'facturacion:categoria_crear' %}" class="btn btn-verde">+ Nueva categoría</a>
</div>
<form method="get" class="d-flex gap-2 mb-3">
    <input type="text" name="q" value="{{ q }}" class="form-control" placeholder="Buscar categoría...">
    <button type="submit" class="btn btn-outline-secondary">Buscar</button>
</form>
<div class="tarjeta p-0 table-responsive">
    <table class="table table-hover align-middle m-0">
        <thead>
            <tr><th>Nombre</th><th>Descripción</th><th class="text-center">Productos</th><th>Estado</th><th class="text-end">Acciones</th></tr>
        </thead>
        <tbody>
            {% for categoria in categorias %}
            <tr>
                <td class="fw-semibold">{{ categoria.nombre }}</td>
                <td>{{ categoria.descripcion|default:"-" }}</td>
                <td class="text-center"><span class="badge bg-light text-dark border">{{ categoria.productos.count }}</span></td>
                <td>
                    {% if categoria.activo %}<span class="badge bg-success">Activa</span>{% else %}<span class="badge bg-secondary">Inactiva</span>{% endif %}
                </td>
                <td class="text-end text-nowrap">
                    <a href="{% url 'facturacion:categoria_editar' categoria.pk %}" class="btn btn-sm btn-outline-primary">Editar</a>
                    <a href="{% url 'facturacion:categoria_eliminar' categoria.pk %}" class="btn btn-sm btn-outline-danger">Eliminar</a>
                </td>
            </tr>
            {% empty %}
            <tr><td colspan="5" class="text-center text-muted py-4">No hay categorías registradas.</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
<p class="text-muted small mt-2">Total: {{ page_obj.paginator.count }} categoría(s)</p>
{% if page_obj.has_other_pages %}
<nav class="mt-3"><ul class="pagination justify-content-center">
    {% if page_obj.has_previous %}
        <li class="page-item"><a class="page-link" href="?page={{ page_obj.previous_page_number }}&q={{ q }}">Anterior</a></li>
    {% endif %}
    <li class="page-item disabled"><span class="page-link">Página {{ page_obj.number }} de {{ page_obj.paginator.num_pages }}</span></li>
    {% if page_obj.has_next %}
        <li class="page-item"><a class="page-link" href="?page={{ page_obj.next_page_number }}&q={{ q }}">Siguiente</a></li>
    {% endif %}
</ul></nav>
{% endif %}
{% endblock %}""",

    "cliente_lista.html": """{% extends "base.html" %}
{% block titulo %}{{ titulo }}{% endblock %}
{% block contenido %}
<div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
    <h1 class="h3 titulo-pagina m-0">{{ titulo }}</h1>
    <a href="{% url 'facturacion:cliente_crear' %}" class="btn btn-verde">+ Nuevo cliente</a>
</div>
<form method="get" class="d-flex gap-2 mb-3">
    <input type="text" name="q" value="{{ q }}" class="form-control" placeholder="Buscar por apellido o cédula...">
    <button type="submit" class="btn btn-outline-secondary">Buscar</button>
</form>
<div class="tarjeta p-0 table-responsive">
    <table class="table table-hover align-middle m-0">
        <thead>
            <tr><th>Cédula</th><th>Cliente</th><th>Correo</th><th>Teléfono</th><th>Dirección</th><th class="text-end">Acciones</th></tr>
        </thead>
        <tbody>
            {% for cliente in clientes %}
            <tr>
                <td>{{ cliente.cedula }}</td>
                <td>
                    <a href="{% url 'facturacion:cliente_detalle' cliente.pk %}" class="fw-semibold text-decoration-none">
                        {{ cliente.apellidos }} {{ cliente.nombres }}
                    </a>
                </td>
                <td>{{ cliente.email|default:"-" }}</td>
                <td>{{ cliente.telefono|default:"-" }}</td>
                <td>{{ cliente.direccion|default:"-" }}</td>
                <td class="text-end text-nowrap">
                    <a href="{% url 'facturacion:cliente_detalle' cliente.pk %}" class="btn btn-sm btn-outline-secondary">Ver</a>
                    <a href="{% url 'facturacion:cliente_editar' cliente.pk %}" class="btn btn-sm btn-outline-primary">Editar</a>
                    <a href="{% url 'facturacion:cliente_eliminar' cliente.pk %}" class="btn btn-sm btn-outline-danger">Eliminar</a>
                </td>
            </tr>
            {% empty %}
            <tr><td colspan="6" class="text-center text-muted py-4">No hay clientes registrados.</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
<p class="text-muted small mt-2">Total: {{ page_obj.paginator.count }} cliente(s)</p>
{% if page_obj.has_other_pages %}
<nav class="mt-3"><ul class="pagination justify-content-center">
    {% if page_obj.has_previous %}
        <li class="page-item"><a class="page-link" href="?page={{ page_obj.previous_page_number }}&q={{ q }}">Anterior</a></li>
    {% endif %}
    <li class="page-item disabled"><span class="page-link">Página {{ page_obj.number }} de {{ page_obj.paginator.num_pages }}</span></li>
    {% if page_obj.has_next %}
        <li class="page-item"><a class="page-link" href="?page={{ page_obj.next_page_number }}&q={{ q }}">Siguiente</a></li>
    {% endif %}
</ul></nav>
{% endif %}
{% endblock %}"""
}

for nombre, contenido in plantillas_extra.items():
    (destino / nombre).write_text(contenido, encoding="utf-8")


# =====================================================================
# PARTE 2: Generador de imágenes reales en carpeta media/ con Pillow
# =====================================================================
def generar_imagen(texto, color_fondo):
    img = Image.new("RGB", (320, 320), color=color_fondo)
    draw = ImageDraw.Draw(img)
    draw.rectangle([16, 16, 304, 304], outline=(255, 255, 255), width=4)
    draw.text((40, 145), texto, fill=(255, 255, 255))
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=90)
    return ContentFile(buffer.getvalue())


# Obtener o crear usuario administrador para el campo user de ModeloBase
usuario = User.objects.first()
if not usuario:
    usuario = User.objects.create_superuser("admin", "admin@mitienda.ec", "admin1234")
    print("Superusuario creado -> usuario: admin | clave: admin1234")

Perfil.objects.get_or_create(
    usuario=usuario,
    defaults={"cedula": "0954321890", "telefono": "0991234567", "cargo": "Administrador", "user": usuario}
)

# 1. Crear 3 Marcas
datos_marcas = [
    ("Samsung", "Corea del Sur"),
    ("Logitech", "Suiza"),
    ("HP", "Estados Unidos"),
]
marcas_obj = {}
for nombre, pais in datos_marcas:
    m, _ = Marca.objects.get_or_create(nombre=nombre, defaults={"pais_origen": pais, "activo": True, "user": usuario})
    marcas_obj[nombre] = m
print(f"Marcas listas: {Marca.objects.count()}")

# 2. Crear 4 Categorías
datos_categorias = [
    ("Smartphones", "Teléfonos móviles y dispositivos Android"),
    ("Laptops", "Computadoras portátiles para trabajo y estudio"),
    ("Periféricos", "Mouses, teclados y accesorios de PC"),
    ("Audio", "Audífonos inalámbricos, monitores in-ear y micrófonos"),
]
cats_obj = {}
for nombre, desc in datos_categorias:
    c, _ = Categoria.objects.get_or_create(nombre=nombre, defaults={"descripcion": desc, "activo": True, "user": usuario})
    cats_obj[nombre] = c
print(f"Categorías listas: {Categoria.objects.count()}")

# 3. Crear 5 Clientes (cédulas de 10 dígitos)
datos_clientes = [
    ("0912345678", "Ana María", "Pérez Torres", "ana.perez@correo.ec", "0991112233", "Av. Quito y 9 de Octubre"),
    ("0923456789", "Luis Alberto", "Mora Castro", "luis.mora@correo.ec", "0992223344", "Cdla. Universitaria"),
    ("0934567890", "Carlos Andrés", "Núñez Álvarez", "carlos.nunez@correo.ec", "0993334455", "Av. 17 de Septiembre"),
    ("0945678901", "Valeria Sofía", "Gómez Vera", "valeria.gomez@correo.ec", "0994445566", "Calle Bolívar y Sucre"),
    ("0956789012", "Jorge Eduardo", "Jaime Mendoza", "jorge.jaime@correo.ec", "0995556677", "Vía Principal Km 2"),
]
clientes_obj = []
for ced, nom, ape, mail, tel, dir_c in datos_clientes:
    cli, _ = Cliente.objects.get_or_create(
        cedula=ced,
        defaults={"nombres": nom, "apellidos": ape, "email": mail, "telefono": tel, "direccion": dir_c, "user": usuario}
    )
    clientes_obj.append(cli)
print(f"Clientes listos: {Cliente.objects.count()}")

# 4. Crear 2 Proveedores con Logo (RUC de 13 dígitos terminado en 001)
datos_proveedores = [
    ("Roberto", "Salazar", "0991234567001", "ventas@tecnoimport.ec", "042556677", "logo_tecno.jpg", (12, 75, 51)),
    ("Elena", "Villamar", "0997654321001", "contacto@digisur.ec", "042889900", "logo_digisur.jpg", (42, 93, 168)),
]
proveedores_obj = []
for nom, ape, ruc, mail, cont, archivo, color in datos_proveedores:
    prov, creado = Proveedor.objects.get_or_create(
        ruc=ruc,
        defaults={"nombre": nom, "apellido": ape, "email": mail, "contacto": cont, "user": usuario}
    )
    if not prov.logo:
        prov.logo.save(archivo, generar_imagen(f"PROVEEDOR\n{nom} {ape}", color), save=True)
    proveedores_obj.append(prov)
print(f"Proveedores con logo listos: {Proveedor.objects.count()}")

# 5. Crear 5 Productos con Foto
datos_productos = [
    ("Galaxy A55", "Smartphone 5G con pantalla AMOLED de 120Hz", Decimal("399.90"), 12, "Samsung", ["Smartphones"], "galaxy_a55.jpg", (20, 60, 120)),
    ("Galaxy Buds FE", "Audífonos inalámbricos con cancelación activa", Decimal("59.90"), 20, "Samsung", ["Audio", "Periféricos"], "galaxy_buds.jpg", (50, 50, 65)),
    ("Logitech G203 Lightsync", "Mouse gamer RGB con sensor óptico de 8000 DPI", Decimal("29.50"), 15, "Logitech", ["Periféricos"], "g203.jpg", (95, 45, 140)),
    ("HP ProBook 640 G8", "Laptop Core i5 11va Gen con 24GB RAM y SSD", Decimal("650.00"), 8, "HP", ["Laptops"], "probook_640.jpg", (15, 90, 80)),
    ("Teclado Mecánico K8", "Teclado retroiluminado con switches táctiles", Decimal("45.00"), 10, "Logitech", ["Periféricos"], "teclado_k8.jpg", (140, 55, 35)),
]
productos_obj = []
for nom, desc, precio, stock, marca_nom, cats_lista, archivo, color in datos_productos:
    prod, creado = Producto.objects.get_or_create(
        nombre=nom,
        defaults={
            "descripcion": desc,
            "precio": precio,
            "stock": stock,
            "marca": marcas_obj[marca_nom],
            "activo": True,
            "user": usuario,
        }
    )
    prod.categorias.set([cats_obj[c] for c in cats_lista])
    if not prod.imagen:
        prod.imagen.save(archivo, generar_imagen(nom, color), save=True)
    productos_obj.append(prod)
print(f"Productos con foto listos: {Producto.objects.count()}")

# 6. Crear 2 Compras con Detalle (si aún no hay compras)
if Compra.objects.count() < 2:
    # Compra 1
    c1 = Compra.objects.create(proveedor=proveedores_obj[0], tipo_pago=TipoPago.CONTADO, user=usuario)
    DetalleCompra.objects.create(compra=c1, producto=productos_obj[0], cantidad=5, precio=Decimal("290.00"), user=usuario)
    DetalleCompra.objects.create(compra=c1, producto=productos_obj[1], cantidad=10, precio=Decimal("38.00"), user=usuario)
    c1.ingresar_stock()
    c1.calcular_totales()

    # Compra 2
    c2 = Compra.objects.create(proveedor=proveedores_obj[1], tipo_pago=TipoPago.TRANSFERENCIA, user=usuario)
    DetalleCompra.objects.create(compra=c2, producto=productos_obj[2], cantidad=8, precio=Decimal("18.50"), user=usuario)
    DetalleCompra.objects.create(compra=c2, producto=productos_obj[3], cantidad=3, precio=Decimal("490.00"), user=usuario)
    c2.ingresar_stock()
    c2.calcular_totales()
print(f"Compras registradas: {Compra.objects.count()}")

# 7. Crear 3 Ventas con Detalle (si aún no hay 3 ventas)
if Venta.objects.count() < 3:
    # Venta 1
    v1 = Venta.objects.create(cliente=clientes_obj[0], tipo_pago=TipoPago.CONTADO, user=usuario)
    DetalleVenta.objects.create(venta=v1, producto=productos_obj[0], cantidad=2, precio=productos_obj[0].precio, user=usuario)
    DetalleVenta.objects.create(venta=v1, producto=productos_obj[1], cantidad=1, precio=productos_obj[1].precio, user=usuario)
    v1.descontar_stock()
    v1.calcular_totales()

    # Venta 2
    v2 = Venta.objects.create(cliente=clientes_obj[1], tipo_pago=TipoPago.TARJETA, user=usuario)
    DetalleVenta.objects.create(venta=v2, producto=productos_obj[3], cantidad=1, precio=productos_obj[3].precio, user=usuario)
    DetalleVenta.objects.create(venta=v2, producto=productos_obj[2], cantidad=2, precio=productos_obj[2].precio, user=usuario)
    v2.descontar_stock()
    v2.calcular_totales()

    # Venta 3
    v3 = Venta.objects.create(cliente=clientes_obj[2], tipo_pago=TipoPago.TRANSFERENCIA, user=usuario)
    DetalleVenta.objects.create(venta=v3, producto=productos_obj[4], cantidad=2, precio=productos_obj[4].precio, user=usuario)
    DetalleVenta.objects.create(venta=v3, producto=productos_obj[2], cantidad=1, precio=productos_obj[2].precio, user=usuario)
    v3.descontar_stock()
    v3.calcular_totales()
print(f"Ventas registradas: {Venta.objects.count()}")

print("\n¡TODO LISTO! Base de datos y carpeta media/ pobladas según el punto 6.6 de la Guía 3.")