from django.http import HttpResponseForbidden
from functools import wraps

def rol_requerido(nombre_rol):
    def decorador(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Debes iniciar sesión.")

            # Accede al rol usando la relación intermedia
            usuario_roles = request.user.usuariorol_set.all()
            if usuario_roles.exists() and usuario_roles.first().rol.nombre_rol == nombre_rol:
                return view_func(request, *args, **kwargs)
            
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
        return _wrapped_view
    return decorador
