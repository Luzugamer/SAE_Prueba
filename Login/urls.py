from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_, name='logout'),
    path('eliminar-cuenta/', views.eliminar_cuenta_view, name='eliminar_cuenta'),
    
    # Rutas para 2FA
    path('verify-2fa/', views.verify_2fa_view, name='verify_2fa'),
    path('setup-2fa/', views.setup_2fa_view, name='setup_2fa'),
    path('disable-2fa/', views.disable_2fa_view, name='disable_2fa'),
    
    # Gestión de dispositivos
    path('dispositivos/', views.dispositivos_view, name='dispositivos'),
    path('dispositivos/confiar/<int:dispositivo_id>/', views.marcar_confiable_view, name='marcar_confiable'),
    path('dispositivos/principal/<int:dispositivo_id>/', views.marcar_principal_view, name='marcar_principal'),
    path('dispositivos/revocar/<int:dispositivo_id>/', views.revocar_dispositivo_view, name='revocar_dispositivo'),
    path('perfil/', views.perfil_usuario_view, name='perfil_usuario'),

]
