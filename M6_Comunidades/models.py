from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
import uuid

ROLES = (
    ('profesor', 'Profesor'),
    ('estudiante', 'Estudiante')
)

ESTADO_MIEMBRO = (
    ('activo', 'Activo'),
    ('inactivo', 'Inactivo'),
)

class Comunidad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    icono = models.ImageField(upload_to='iconos/', null=True, blank=True)
    institucion_afiliada = models.CharField(max_length=200, blank=True, null=True)
    creador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comunidades_creadas')
    miembros = models.ManyToManyField(settings.AUTH_USER_MODEL, through='MiembroComunidad', related_name='comunidades')
    puntos_prestigio = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    es_destacada = models.BooleanField(default=False)
    codigo_invitacion = models.CharField(max_length=10, unique=True, blank=True)
    activa = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.codigo_invitacion:
            self.codigo_invitacion = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def get_miembros_activos(self):
        return self.miembrocomunidad_set.filter(estado='activo')

    def get_miembros_inactivos(self):
        return self.miembrocomunidad_set.filter(estado='inactivo')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Comunidades"

class MiembroComunidad(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)
    fecha_union = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADO_MIEMBRO, default='activo')
    rol = models.CharField(max_length=10, choices=ROLES, default='estudiante')

    class Meta:
        unique_together = ['usuario', 'comunidad']

class Mensaje(models.Model):
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE, related_name='mensajes')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contenido = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    es_importante = models.BooleanField(default=False)

    def es_vigente(self):
        return self.timestamp >= timezone.now() - timedelta(weeks=2)

    def __str__(self):
        return f"{self.autor.username}: {self.contenido[:30]}"

    class Meta:
        ordering = ['-timestamp']

class Perfil(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')
    rol = models.CharField(max_length=10, choices=ROLES, default='estudiante')
    institucion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_display()}"

class Invitacion(models.Model):
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)
    invitado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invitaciones_enviadas')
    invitado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invitaciones_recibidas')
    fecha_invitacion = models.DateTimeField(auto_now_add=True)
    aceptada = models.BooleanField(default=False)
    procesada = models.BooleanField(default=False)

    class Meta:
        unique_together = ['comunidad', 'invitado']

class Reporte(models.Model):
    MOTIVOS = (
        ('spam', 'Spam'),
        ('contenido_inapropiado', 'Contenido inapropiado'),
        ('acoso', 'Acoso'),
        ('otro', 'Otro'),
    )
    
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)
    reportado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    motivo = models.CharField(max_length=80, choices=MOTIVOS)
    descripcion = models.TextField()
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    procesado = models.BooleanField(default=False)

    def __str__(self):
        return f"Reporte de {self.reportado_por.username} sobre {self.comunidad.nombre}"