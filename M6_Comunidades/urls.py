from django.urls import path
from . import views

app_name = 'comunidad'

urlpatterns = [
    # Página principal
    path('inicio', views.home, name='inicio'),
    path('principio', views.principio, name='principio'),

    # Gestión de comunidades
    path('mis-comunidades/', views.mis_comunidades, name='mis_comunidad'),
    path('crear/', views.crear_comunidad, name='crear_comunidad'),
    path('<int:comunidad_id>/', views.comunidad_detalle, name='comunidad_detalle'),
    path('<int:comunidad_id>/editar/', views.editar_comunidad, name='editar_comunidad'),
    path('<int:comunidad_id>/eliminar/', views.eliminar_comunidad, name='eliminar_comunidad'),
    # Membresía 
    path('<int:comunidad_id>/unirse/', views.unirse_comunidad, name='unirse_comunidad'),
    path('<int:comunidad_id>/salir/', views.salir_comunidad, name='salir_comunidad'),
    path('invitacion/<str:codigo_invitacion>/', views.unirse_por_invitacion, name='unirse_por_invitacion'),
    
    path('<int:comunidad_id>/invitar/', views.invitar_estudiantes, name='invitar_estudiantes'),
    path('<int:comunidad_id>/gestionar-miembros/', views.gestionar_miembros, name='gestionar_miembros'),
    path('<int:comunidad_id>/compartir/', views.compartir_comunidad, name='compartir_comunidad'),
 path('verificar-nombre/', views.verificar_nombre_comunidad, name='verificar_nombre_comunidad'),
    # Funcionalidades especiales
    path('<int:comunidad_id>/zona_descanso/', views.zona_descanso, name='zona_descanso'),
    path('<int:comunidad_id>/reportar/', views.reportar_comunidad, name='reportar_comunidad'),
    
    # Búsqueda y navegación
    path('buscar/', views.buscar_comunidades, name='buscar_comunidades'),
    path('crear/', views.crear_comunidad, name='crear_comunidad'),
    path('comunidad/', views.comunidad, name='comunidad'),

    # Asistente IA
    path('asistente-ia/', views.asistente_ia, name='asistente_ia'),
    
]