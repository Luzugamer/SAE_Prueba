from django.apps import AppConfig

class M3ModuloDeExamenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'M3_modulo_de_examen'  # Cambia por el nombre real de tu app
    verbose_name = 'Módulo de Exámenes'
    
    def ready(self):
        """
        Se ejecuta cuando Django ha cargado completamente la aplicación
        """
        try:
            import M3_modulo_de_examen.signals  # Cambia por tu app
        except ImportError:
            pass