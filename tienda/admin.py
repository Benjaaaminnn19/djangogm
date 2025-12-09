from django.contrib import admin
from .models import Producto

# Register your models here.

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio', 'stock', 'activo']
    list_filter = ['categoria', 'activo']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['precio', 'stock', 'activo']

    def precio_clp(self, obj):
        return f"${obj.precio:,}".replace(",", ".")
    precio_clp.short_description = "Precio (CLP)"
