from django.urls import path
from . import views

urlpatterns = [
    path('', views.tienda, name='tienda'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('test/', views.tienda_test, name='tienda_test'),
    path('simple/', views.tienda_simple, name='tienda_simple'),
    path('raw/', views.tienda_raw, name='tienda_raw'),
]
