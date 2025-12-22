from django.contrib import admin
from .models import Producto, ImagenProducto
from django.contrib.humanize.templatetags.humanize import intcomma

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 3  # Número de formularios vacíos para agregar imágenes
    fields = ['imagen', 'orden', 'es_principal']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    inlines = [ImagenProductoInline]  # ESTO es lo importante para las múltiples imágenes
    list_display = ['nombre', 'categoria', 'precio', 'stock', 'activo']
    list_filter = ['categoria', 'activo']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['precio', 'stock', 'activo']

    def precio_clp(self, obj):
        return f"${intcomma(obj.precio)}"
    precio_clp.short_description = "Precio (CLP)"