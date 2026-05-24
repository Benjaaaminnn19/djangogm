from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from .sitemaps import EstaticasSitemap, ProductoSitemap
from . import views

sitemaps = {
    'estaticas': EstaticasSitemap,
    'productos': ProductoSitemap,
}

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
    path('verificar-email/<str:token>/', views.verificar_email, name='verificar_email'),
    path('reenviar-verificacion/', views.reenviar_verificacion, name='reenviar_verificacion'),

    # Portal y dashboard
    path('portal/', views.portal_miembro, name='portal_miembro'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Páginas legales
    path('privacidad/', views.privacidad, name='privacidad'),
    path('terminos/', views.terminos, name='terminos'),

    # SEO
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # Recuperación de contraseña (vistas built-in de Django)
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html',
        email_template_name='emails/password_reset_email.txt',
        html_email_template_name='emails/password_reset_email.html',
        subject_template_name='emails/password_reset_subject.txt',
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html',
    ), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html',
    ), name='password_reset_complete'),
]


