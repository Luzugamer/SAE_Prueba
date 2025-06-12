from django.apps import AppConfig


class M6ComunidadesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'M6_Comunidades'
    verbose_name = 'Comunidades de Estudio'
    
    def ready(self):
        import M6_Comunidades.signals
