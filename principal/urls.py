from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('registrar-lead/', views.RegistrarLeadView.as_view(), name='registrar_lead'),
]


