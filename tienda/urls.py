from django.urls import path
from . import views

urlpatterns = [
    path('', views.tienda, name='tienda'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('pago/iniciar/', views.iniciar_pago, name='iniciar_pago'),
    path('pago/confirmar/', views.confirmar_pago, name='confirmar_pago'),
    path('pago/resultado/', views.resultado_pago, name='resultado_pago'),


]
