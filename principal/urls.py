from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),  # NUEVA RUTA
    path('logout/', views.logout_view, name='logout'),  # NUEVA RUTA
    path('checkin/', views.checkin_view, name='checkin'),  # Ahora requiere login
    path('clases/', views.listar_clases, name='listar_clases'),
    path('agendar/<int:clase_id>/', views.agendar_clase, name='agendar_clase'),
    path('invitaciones/', views.invitaciones_confirmadas, name='invitaciones_confirmadas'),
    path('api/registrar-lead/', views.RegistrarLeadView.as_view(), name='registrar_lead'),
    path('api/comprar-plan/', views.ComprarPlanView.as_view(), name='comprar_plan'),
]


