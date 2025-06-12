from django.contrib import admin
from .models import Comunidad, Mensaje, Perfil, MiembroComunidad, Invitacion, Reporte

@admin.register(Comunidad)
class ComunidadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'creador', 'puntos_prestigio', 'es_destacada', 'fecha_creacion', 'activa']
    list_filter = ['es_destacada', 'activa', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion', 'institucion_afiliada']
    readonly_fields = ['codigo_invitacion', 'fecha_creacion']

@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ['autor', 'comunidad', 'timestamp', 'es_importante']
    list_filter = ['timestamp', 'es_importante']
    search_fields = ['contenido', 'autor__username']

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'rol', 'institucion']
    list_filter = ['rol']
    search_fields = ['usuario__username', 'institucion']

@admin.register(MiembroComunidad)
class MiembroComunidadAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'comunidad', 'rol', 'estado', 'fecha_union']
    list_filter = ['rol', 'estado', 'fecha_union']

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ['reportado_por', 'comunidad', 'motivo', 'fecha_reporte', 'procesado']
    list_filter = ['motivo', 'procesado', 'fecha_reporte']