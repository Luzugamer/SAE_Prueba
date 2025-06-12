from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Perfil

@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def save_perfil(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
    else:
        Perfil.objects.create(usuario=instance)
