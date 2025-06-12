from django.urls import path
from . import views

urlpatterns = [
    path('curso/<str:curso_codigo>/examenes/', views.lista_examenes_curso, name='lista_examenes_curso'),
    path('curso/<str:curso_codigo>/crear-examen/', views.crear_examen, name='crear_examen'),
    path('examen/<int:examen_id>/eliminar/', views.eliminar_examen, name='eliminar_examen'),
    path('examen/<int:examen_id>/agregar-preguntas/', views.agregar_preguntas, name='agregar_preguntas'),
    path('examen/<int:examen_id>/responder/', views.responder_examen, name='responder_examen'),
    path('examen/<int:examen_id>/resultado/', views.resultado_examen, name='resultado_examen'),
    path('examen/<int:examen_id>/estadisticas/', views.estadisticas_examen, name='estadisticas_examen'),
]