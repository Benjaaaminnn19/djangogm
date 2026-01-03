from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home, name='home'),
    path('registrar-lead/', views.RegistrarLeadView.as_view(), name='registrar_lead'),
    path('clases/', views.listar_clases, name='listar_clases'),
    path('agendar/<int:clase_id>/', views.agendar_clase, name='agendar_clase'),
    path('invitaciones/', views.invitaciones_confirmadas, name='invitaciones_confirmadas'),
    path('comprar-plan/', views.ComprarPlanView.as_view(), name='comprar_plan'),
    path('checkin/', views.checkin_view, name='checkin'),
    path('registro/', views.registro_view, name='registro'),
]


