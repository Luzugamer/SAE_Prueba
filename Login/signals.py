from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Rol

@receiver(post_migrate)
def crear_roles_por_defecto(sender, **kwargs):
    roles = [
        ('estudiante', 'Rol para estudiantes'),
        ('profesor', 'Rol para profesores'),
    ]

    for nombre_rol, descripcion in roles:
        Rol.objects.get_or_create(nombre_rol=nombre_rol, defaults={'descripcion': descripcion})
