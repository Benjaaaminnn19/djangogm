from django.urls import path
from . import views

urlpatterns = [
    path('', views.tienda, name='tienda'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),

]
