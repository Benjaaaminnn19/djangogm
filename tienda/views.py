from django.shortcuts import render, get_object_or_404
from .models import Producto

def formatear_precio(precio):
    """Formatea precio al estilo chileno: 27900 -> $27.900"""
    try:
        return f"${int(precio):,}".replace(',', '.')
    except (ValueError, TypeError):
        return f"${precio}"

def tienda(request):
    """Vista principal de la tienda"""
    productos = Producto.objects.all()
    for producto in productos:
        producto.precio_formateado = formatear_precio(producto.precio)
    return render(request, 'tienda.html', {'productos': productos})

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.precio_formateado = formatear_precio(producto.precio)
    
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        activo=True
    ).exclude(id=producto_id)[:3]
    
    for prod in productos_relacionados:
        prod.precio_formateado = formatear_precio(prod.precio)

    return render(request, 'detalle_producto.html', {
        'producto': producto,
        'productos_relacionados': productos_relacionados
    })