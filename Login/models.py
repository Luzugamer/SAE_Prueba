from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import pyotp
import qrcode
from io import BytesIO
import base64


class UsuarioManager(BaseUserManager):
    def create_user(self, correo_electronico, nombre, apellido, password=None, **extra_fields):
        if not correo_electronico:
            raise ValueError("El correo electrónico es obligatorio")
        correo_electronico = self.normalize_email(correo_electronico)
        user = self.model(correo_electronico=correo_electronico, nombre=nombre, apellido=apellido, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        # Asignar rol por defecto "estudiante" solo si no es staff/superuser
        if not user.is_staff and not user.is_superuser:
            rol_estudiante, created = Rol.objects.get_or_create(
                nombre_rol='estudiante',
                defaults={'descripcion': 'Rol por defecto para estudiantes'}
            )
            UsuarioRol.objects.create(usuario=user, rol=rol_estudiante)
        
        return user

    def create_superuser(self, correo_electronico, nombre, apellido, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        user = self.create_user(correo_electronico, nombre, apellido, password, **extra_fields)
        
        # Asignar rol de admin al superusuario
        rol_admin, created = Rol.objects.get_or_create(
            nombre_rol='admin',
            defaults={'descripcion': 'Administrador del sistema'}
        )
        UsuarioRol.objects.create(usuario=user, rol=rol_admin)
        
        return user


class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    correo_electronico = models.EmailField(unique=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    ultima_sesion = models.DateTimeField(null=True, blank=True)
    cierre_sesion = models.DateTimeField(null=True, blank=True)
    
    # Campos para 2FA
    otp_secret_key = models.CharField(max_length=32, blank=True, null=True)
    is_two_factor_enabled = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'correo_electronico'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    def generate_otp_secret(self):
        """Genera una clave secreta para OTP"""
        if not self.otp_secret_key:
            self.otp_secret_key = pyotp.random_base32()
            self.save()
        return self.otp_secret_key
    
    def get_otp_uri(self):
        """Genera URI para código QR de autenticación"""
        if not self.otp_secret_key:
            self.generate_otp_secret()
        
        totp = pyotp.TOTP(self.otp_secret_key)
        return totp.provisioning_uri(
            name=self.correo_electronico,
            issuer_name="Tu Sistema Académico"
        )
    
    def get_qr_code(self):
        """Genera código QR en base64 para configurar 2FA"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(self.get_otp_uri())
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def verify_otp(self, otp_code):
        """Verifica el código OTP ingresado"""
        if not self.otp_secret_key:
            return False
        
        totp = pyotp.TOTP(self.otp_secret_key)
        return totp.verify(otp_code, valid_window=1)


class Rol(models.Model):
    nombre_rol = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre_rol


class UsuarioRol(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('usuario', 'rol')


class DispositivoUsuario(models.Model):
    """Modelo para trackear dispositivos de usuarios"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='dispositivos')
    nombre_dispositivo = models.CharField(max_length=255, blank=True)
    user_agent = models.TextField()
    ip_address = models.GenericIPAddressField()
    fingerprint = models.CharField(max_length=64, unique=True)
    es_confiable = models.BooleanField(default=False)
    es_principal = models.BooleanField(default=False)
    primer_acceso = models.DateTimeField(auto_now_add=True)
    ultimo_acceso = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    # Información adicional del dispositivo
    sistema_operativo = models.CharField(max_length=100, blank=True)
    navegador = models.CharField(max_length=100, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    pais = models.CharField(max_length=100, blank=True)
    
    class Meta:
        unique_together = ('usuario', 'fingerprint')
    
    def __str__(self):
        return f"{self.usuario.correo_electronico} - {self.nombre_dispositivo or 'Dispositivo desconocido'}"


class NotificacionSeguridad(models.Model):
    """Modelo para notificaciones de seguridad"""
    TIPOS_NOTIFICACION = [
        ('nuevo_dispositivo', 'Nuevo Dispositivo'),
        ('inicio_sesion_sospechoso', 'Inicio de Sesión Sospechoso'),
        ('2fa_habilitado', '2FA Habilitado'),
        ('2fa_deshabilitado', '2FA Deshabilitado'),
        ('cambio_password', 'Cambio de Contraseña'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones_seguridad')
    tipo = models.CharField(max_length=30, choices=TIPOS_NOTIFICACION)
    titulo = models.CharField(max_length=255)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Información adicional
    ip_origen = models.GenericIPAddressField(null=True, blank=True)
    dispositivo = models.ForeignKey(DispositivoUsuario, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.usuario.correo_electronico} - {self.titulo}"