import requests
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Obtiene la IP real del cliente considerando proxies"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_location_from_ip(ip_address):
    """
    Obtiene información de ubicación basada en la IP
    Usa un servicio gratuito de geolocalización
    """
    if ip_address in ['127.0.0.1', 'localhost', '::1']:
        return {
            'ciudad': 'Local',
            'pais': 'Local',
            'region': 'Local'
        }
    
    try:
        # Usando ipapi.co (servicio gratuito)
        response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'ciudad': data.get('city', 'Desconocida'),
                'pais': data.get('country_name', 'Desconocido'),
                'region': data.get('region', 'Desconocida')
            }
    except Exception as e:
        logger.warning(f"Error obteniendo ubicación para IP {ip_address}: {e}")
    
    return {
        'ciudad': 'Desconocida',
        'pais': 'Desconocido',
        'region': 'Desconocida'
    }


def enviar_notificacion_email(usuario, asunto, mensaje):
    """
    Envía una notificación por email al usuario
    """
    try:
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[usuario.correo_electronico],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Error enviando email a {usuario.correo_electronico}: {e}")
        return False


def generar_codigo_backup():
    """
    Genera códigos de backup para 2FA (opcional)
    """
    import secrets
    import string
    
    codes = []
    for _ in range(10):
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        codes.append(f"{code[:4]}-{code[4:]}")
    
    return codes


def validar_fuerza_password(password):
    """
    Valida la fuerza de una contraseña
    Retorna un diccionario con el score y recomendaciones
    """
    import re
    
    score = 0
    feedback = []
    
    # Longitud
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Debe tener al menos 8 caracteres")
    
    if len(password) >= 12:
        score += 1
    
    # Caracteres especiales
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("Debe incluir al menos una letra mayúscula")
    
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("Debe incluir al menos una letra minúscula")
    
    if re.search(r'[0-9]', password):
        score += 1
    else:
        feedback.append("Debe incluir al menos un número")
    
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        feedback.append("Debe incluir al menos un carácter especial")
    
    # Palabras comunes (básico)
    palabras_comunes = ['password', '123456', 'qwerty', 'admin', 'usuario']
    if any(palabra in password.lower() for palabra in palabras_comunes):
        score -= 1
        feedback.append("Evita usar palabras comunes")
    
    # Determinar nivel de seguridad
    if score >= 5:
        nivel = "Fuerte"
    elif score >= 3:
        nivel = "Medio"
    else:
        nivel = "Débil"
    
    return {
        'score': max(0, score),
        'nivel': nivel,
        'feedback': feedback
    }


def detectar_patron_login_sospechoso(usuario, ip_actual):
    """
    Detecta patrones de login sospechosos
    """
    from django.utils import timezone
    from datetime import timedelta
    
    # Verificar intentos desde múltiples IPs en poco tiempo
    ahora = timezone.now()
    hace_una_hora = ahora - timedelta(hours=1)
    
    dispositivos_recientes = usuario.dispositivos.filter(
        ultimo_acceso__gte=hace_una_hora
    ).values_list('ip_address', flat=True).distinct()
    
    # Si hay más de 3 IPs diferentes en la última hora
    if len(dispositivos_recientes) > 3:
        return True, "Múltiples ubicaciones en poco tiempo"
    
    # Verificar si es una IP de un país muy diferente al habitual
    # (implementación básica - podrías mejorarlo con más lógica)
    ubicaciones_habituales = usuario.dispositivos.filter(
        ultimo_acceso__gte=ahora - timedelta(days=30)
    ).values_list('pais', flat=True).distinct()
    
    ubicacion_actual = get_location_from_ip(ip_actual)
    if (len(ubicaciones_habituales) > 0 and 
        ubicacion_actual['pais'] not in ubicaciones_habituales and 
        ubicacion_actual['pais'] != 'Local'):
        return True, f"Acceso desde ubicación inusual: {ubicacion_actual['pais']}"
    
    return False, None