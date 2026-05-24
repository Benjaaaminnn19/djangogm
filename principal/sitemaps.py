from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from tienda.models import Producto


class EstaticasSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return [
            'home',
            'listar_clases',
            'tienda',
            'login',
            'registro',
            'privacidad',
            'terminos',
        ]

    def location(self, item):
        return reverse(item)


class ProductoSitemap(Sitemap):
    priority = 0.6
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return Producto.objects.filter(activo=True)

    def location(self, obj):
        return reverse('detalle_producto', args=[obj.pk])
