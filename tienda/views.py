from django.shortcuts import render, get_object_or_404
from .models import Producto

def tienda(request):
    """Vista principal de la tienda"""
    productos = Producto.objects.all()
    return render(request, 'tienda.html', {'productos': productos})

def detalle_producto(request, producto_id):
    """Vista para mostrar el detalle de un producto"""
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'detalle_producto.html', {'producto': producto})

def tienda_test(request):
    """Vista de prueba para la tienda"""
    productos = Producto.objects.all()
    return render(request, 'tienda_test.html', {'productos': productos})

def tienda_simple(request):
    """Vista simple de la tienda"""
    productos = Producto.objects.all()
    return render(request, 'tienda_simple.html', {'productos': productos})

def tienda_raw(request):
    """Vista raw de la tienda"""
    productos = Producto.objects.all()
    return render(request, 'tienda_minimal.html', {'productos': productos})
