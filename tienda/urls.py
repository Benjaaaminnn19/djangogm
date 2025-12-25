from django.urls import path
from . import views


urlpatterns = [
    path('', views.tienda, name='tienda'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('pago/iniciar/<int:producto_id>/', views.iniciar_pago, name='iniciar_pago'),
    path('pago/confirmar/', views.confirmar_pago, name='confirmar_pago'),
    path('pago/resultados/', views.resultado_pago, name='resultado_pago'),
    path('return/', views.return_view, name='payment_return'),
    path('pago/multiplo/', views.pago_multiplo, name='pago_multiplo'),

]