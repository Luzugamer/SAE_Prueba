from django.apps import AppConfig

class LoginConfig(AppConfig):
    name = 'Login'

    def ready(self):
        import Login.signals
