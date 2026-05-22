from django.contrib import admin
from django import forms
from .models import Producto, ImagenProducto
from django.contrib.humanize.templatetags.humanize import intcomma


class ImagenProductoForm(forms.ModelForm):
    """
    Usa FileInput en lugar de ClearableFileInput para evitar que el checkbox
    "Clear" del widget estándar borre accidentalmente imágenes de Cloudinary.
    """
    class Meta:
        model = ImagenProducto
        fields = ['imagen', 'orden', 'es_principal']
        widgets = {
            'imagen': forms.FileInput(),
        }


class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    form = ImagenProductoForm
    extra = 1
    # can_delete=False evita que un clic accidental en "Delete" borre la imagen de Cloudinary
    can_delete = False
    fields = ['imagen', 'orden', 'es_principal']

    def get_extra(self, request, obj=None, **kwargs):
        # Si el producto ya tiene imágenes, no mostrar formularios vacíos extra
        if obj and obj.imagenes.exists():
            return 0
        return 1


@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    """
    Admin separado para gestionar imágenes de forma explícita y segura.
    Úsalo cuando necesites borrar o reemplazar imágenes específicas.
    """
    list_display = ['producto', 'orden', 'es_principal']
    list_filter = ['producto', 'es_principal']
    form = ImagenProductoForm


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    inlines = [ImagenProductoInline]
    list_display = ['nombre', 'categoria', 'precio', 'stock', 'activo']
    list_filter = ['categoria', 'activo']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['precio', 'stock', 'activo']

    def precio_clp(self, obj):
        return f"${intcomma(obj.precio)}"
    precio_clp.short_description = "Precio (CLP)"