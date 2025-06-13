from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
import hashlib
import json
from user_agents import parse
from .utils import detectar_patron_login_sospechoso

from .forms import UsuarioRegistroForm, UsuarioLoginForm, OTPVerificationForm, Setup2FAForm, DispositivoConfiableForm, CambiarPasswordForm
from .models import UsuarioRol, Usuario, DispositivoUsuario, NotificacionSeguridad
from .utils import get_client_ip, get_location_from_ip, enviar_notificacion_email
from django.contrib.auth import update_session_auth_hash

def get_device_fingerprint(request):
    """Genera un fingerprint único del dispositivo"""
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
    
    # Crear fingerprint basado en varios factores
    fingerprint_data = f"{user_agent}{accept_language}{accept_encoding}"
    return hashlib.sha256(fingerprint_data.encode()).hexdigest()

def parse_user_agent(user_agent_string):
    """Parsea el user agent para extraer información del dispositivo"""
    user_agent = parse(user_agent_string)
    return {
        'navegador': f"{user_agent.browser.family} {user_agent.browser.version_string}",
        'sistema_operativo': f"{user_agent.os.family} {user_agent.os.version_string}",
        'es_mobile': user_agent.is_mobile,
        'es_tablet': user_agent.is_tablet,
        'es_pc': user_agent.is_pc
    }

def verificar_dispositivo(request, usuario):
    """Verifica si el dispositivo es conocido y confiable"""
    fingerprint = get_device_fingerprint(request)
    ip_address = get_client_ip(request)
    
    try:
        dispositivo = DispositivoUsuario.objects.get(
            usuario=usuario, 
            fingerprint=fingerprint
        )
        # Actualizar último acceso
        dispositivo.ultimo_acceso = timezone.now()
        dispositivo.ip_address = ip_address
        dispositivo.save()
        return dispositivo, False  # Dispositivo conocido
    except DispositivoUsuario.DoesNotExist:
        # Dispositivo nuevo
        user_agent_info = parse_user_agent(request.META.get('HTTP_USER_AGENT', ''))
        location_info = get_location_from_ip(ip_address)
        
        dispositivo = DispositivoUsuario.objects.create(
            usuario=usuario,
            fingerprint=fingerprint,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            ip_address=ip_address,
            navegador=user_agent_info['navegador'],
            sistema_operativo=user_agent_info['sistema_operativo'],
            ciudad=location_info.get('ciudad', ''),
            pais=location_info.get('pais', ''),
            nombre_dispositivo=f"{user_agent_info['sistema_operativo']} - {user_agent_info['navegador']}"
        )
        
        # Crear notificación de nuevo dispositivo
        NotificacionSeguridad.objects.create(
            usuario=usuario,
            tipo='nuevo_dispositivo',
            titulo='Nuevo dispositivo detectado',
            mensaje=f'Se ha detectado un inicio de sesión desde un nuevo dispositivo: {dispositivo.nombre_dispositivo}',
            ip_origen=ip_address,
            dispositivo=dispositivo
        )
        
        # Enviar email de notificación
        enviar_notificacion_nuevo_dispositivo(usuario, dispositivo)
        
        return dispositivo, True  # Dispositivo nuevo

def enviar_notificacion_nuevo_dispositivo(usuario, dispositivo):
    """Envía notificación por email de nuevo dispositivo"""
    subject = 'Nuevo dispositivo detectado en tu cuenta'
    message = f"""
    Hola {usuario.nombre},
    
    Se ha detectado un inicio de sesión desde un nuevo dispositivo:
    
    Dispositivo: {dispositivo.nombre_dispositivo}
    Ubicación: {dispositivo.ciudad}, {dispositivo.pais}
    Fecha y hora: {dispositivo.primer_acceso.strftime('%d/%m/%Y %H:%M:%S')}
    
    Si fuiste tú, puedes ignorar este mensaje.
    Si no reconoces este inicio de sesión, te recomendamos cambiar tu contraseña inmediatamente.
    
    Saludos,
    Equipo de Seguridad
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [usuario.correo_electronico],
        fail_silently=True,
    )

def registro_view(request):
    if request.method == 'POST':
        form = UsuarioRegistroForm(request.POST)
        if form.is_valid():
            user = Usuario.objects.create_user(
                correo_electronico=form.cleaned_data['correo_electronico'],
                nombre=form.cleaned_data['nombre'],
                apellido=form.cleaned_data['apellido'],
                password=form.cleaned_data['password']
            )
            messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = UsuarioRegistroForm()
    return render(request, 'Login/registro.html', {'form': form})

def enviar_alerta_actividad_sospechosa(usuario, motivo, dispositivo):
    """Envía alerta por email de actividad sospechosa"""
    subject = '⚠️ Actividad sospechosa en tu cuenta'
    message = f"""
    Hola {usuario.nombre},
    
    Se ha detectado actividad sospechosa en tu cuenta:
    
    Motivo: {motivo}
    Dispositivo: {dispositivo.nombre_dispositivo}
    Ubicación: {dispositivo.ciudad}, {dispositivo.pais}
    Fecha y hora: {dispositivo.ultimo_acceso.strftime('%d/%m/%Y %H:%M:%S')}
    IP: {dispositivo.ip_address}
    
    Si fuiste tú, puedes ignorar este mensaje.
    Si no reconoces esta actividad, te recomendamos:
    1. Cambiar tu contraseña inmediatamente
    2. Revisar tus dispositivos confiables
    3. Habilitar la autenticación de dos factores
    
    Saludos,
    Equipo de Seguridad
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [usuario.correo_electronico],
        fail_silently=True,
    )

def login_view(request):
    if request.method == 'POST':
        form = UsuarioLoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo_electronico']
            password = form.cleaned_data['password']

            user = authenticate(request, correo_electronico=correo, password=password)

            if user is not None:
                # Verificar dispositivo
                dispositivo, es_nuevo = verificar_dispositivo(request, user)
                
                # Detectar patrones sospechosos
                ip_actual = get_client_ip(request)
                es_sospechoso, motivo = detectar_patron_login_sospechoso(user, ip_actual)
                
                if es_sospechoso:
                    # Crear notificación de actividad sospechosa
                    NotificacionSeguridad.objects.create(
                        usuario=user,
                        tipo='inicio_sesion_sospechoso',
                        titulo='Actividad sospechosa detectada',
                        mensaje=f'Se detectó actividad sospechosa: {motivo}',
                        ip_origen=ip_actual,
                        dispositivo=dispositivo
                    )
                    
                    # Enviar email de alerta
                    enviar_alerta_actividad_sospechosa(user, motivo, dispositivo)
                
                # Si tiene 2FA habilitado y el dispositivo no es confiable
                if user.is_two_factor_enabled and not dispositivo.es_confiable:
                    # Almacenar datos en sesión para la verificación 2FA
                    request.session['pre_2fa_user_id'] = user.id
                    request.session['pre_2fa_device_id'] = dispositivo.id
                    return redirect('verify_2fa')
                
                # Login directo si no tiene 2FA o dispositivo es confiable
                return complete_login(request, user, dispositivo)
            else:
                form.add_error(None, 'Correo electrónico o contraseña inválidos.')
    else:
        form = UsuarioLoginForm()

    return render(request, 'Login/login.html', {'form': form})

@login_required
def eliminar_cuenta_view(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Tu cuenta ha sido eliminada exitosamente.')
        return redirect('descripcion')  # o 'login' según prefieras

    return redirect('perfil_usuario')

def verify_2fa_view(request):
    """Vista para verificar código 2FA"""
    if 'pre_2fa_user_id' not in request.session:
        return redirect('login')
    
    user_id = request.session['pre_2fa_user_id']
    device_id = request.session['pre_2fa_device_id']
    user = get_object_or_404(Usuario, id=user_id)
    dispositivo = get_object_or_404(DispositivoUsuario, id=device_id)
    
    if request.method == 'POST':
        otp_form = OTPVerificationForm(request.POST)
        trust_form = DispositivoConfiableForm(request.POST)
        
        if otp_form.is_valid():
            otp_code = otp_form.cleaned_data['otp_code']
            
            if user.verify_otp(otp_code):
                # Código correcto
                if trust_form.is_valid() and trust_form.cleaned_data.get('marcar_confiable'):
                    dispositivo.es_confiable = True
                    dispositivo.save()
                
                # Limpiar sesión temporal
                del request.session['pre_2fa_user_id']
                del request.session['pre_2fa_device_id']
                
                return complete_login(request, user, dispositivo)
            else:
                otp_form.add_error('otp_code', 'Código de verificación incorrecto.')
    else:
        otp_form = OTPVerificationForm()
        trust_form = DispositivoConfiableForm()
    
    return render(request, 'Login/verify_2fa.html', {
        'otp_form': otp_form,
        'trust_form': trust_form,
        'user': user
    })

def complete_login(request, user, dispositivo):
    """Completa el proceso de login"""
    try:
        usuario_rol = UsuarioRol.objects.get(usuario=user)
        rol_usuario = usuario_rol.rol.nombre_rol
        
        user.ultima_sesion = timezone.now()
        user.save()
        login(request, user)
        
        # Redireccionar según rol
        if rol_usuario == 'admin':
            return redirect('/admin/')
        elif rol_usuario == 'profesor':
            return redirect('pag_profe')
        elif rol_usuario == 'estudiante':
            return redirect('pag_estu')
        else:
            return redirect('pag_estu')
            
    except UsuarioRol.DoesNotExist:
        messages.error(request, 'Usuario sin rol asignado. Contacte al administrador.')
        return redirect('login')

@login_required
def cerrar_sesion_dispositivo_view(request, dispositivo_id):
    dispositivo = get_object_or_404(DispositivoUsuario, id=dispositivo_id, usuario=request.user)

    if dispositivo.es_principal:
        messages.error(request, "No puedes cerrar sesión del dispositivo principal.")
        return redirect('dispositivos')

    if request.method == 'POST':
        dispositivo.activo = False
        dispositivo.save()
        messages.success(request, "Sesión cerrada correctamente para el dispositivo.")
        return redirect('dispositivos')
    
    return redirect('dispositivos')


@login_required
def setup_2fa_view(request):
    """Vista para configurar 2FA"""
    user = request.user
    
    if request.method == 'POST':
        form = Setup2FAForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp_code']
            
            if user.verify_otp(otp_code):
                user.is_two_factor_enabled = True
                user.save()
                
                # Crear notificación
                NotificacionSeguridad.objects.create(
                    usuario=user,
                    tipo='2fa_habilitado',
                    titulo='Autenticación de dos factores habilitada',
                    mensaje='Has habilitado exitosamente la autenticación de dos factores en tu cuenta.'
                )
                
                messages.success(request, 'Autenticación de dos factores habilitada correctamente.')
                return redirect('perfil_usuario')  # Redireccionar a página de perfil
            else:
                form.add_error('otp_code', 'Código de verificación incorrecto.')
    else:
        form = Setup2FAForm()
        # Generar secret si no existe
        user.generate_otp_secret()
    
    qr_code = user.get_qr_code()
    
    return render(request, 'Login/setup_2fa.html', {
        'form': form,
        'qr_code': qr_code,
        'secret_key': user.otp_secret_key
    })

@login_required
def disable_2fa_view(request):
    """Vista para deshabilitar 2FA"""
    if request.method == 'POST':
        user = request.user
        user.is_two_factor_enabled = False
        user.otp_secret_key = None
        user.save()
        
        # Crear notificación
        NotificacionSeguridad.objects.create(
            usuario=user,
            tipo='2fa_deshabilitado',
            titulo='Autenticación de dos factores deshabilitada',
            mensaje='Has deshabilitado la autenticación de dos factores en tu cuenta.'
        )
        
        messages.success(request, 'Autenticación de dos factores deshabilitada.')
        return redirect('perfil_usuario')
    
    return render(request, 'Login/disable_2fa.html')

@login_required
def dispositivos_view(request):
    dispositivos = request.user.dispositivos.filter(activo=True).order_by('-ultimo_acceso')
    hay_principal = dispositivos.filter(es_principal=True).exists()

    return render(request, 'Login/dispositivos_confiables.html', {
        'dispositivos': dispositivos,
        'hay_principal': hay_principal
    })


@login_required
def marcar_confiable_view(request, dispositivo_id):
    dispositivo = get_object_or_404(
        DispositivoUsuario,
        id=dispositivo_id,
        usuario=request.user
    )

    if request.method == 'POST':
        dispositivo.es_confiable = True
        dispositivo.save()

        messages.success(request, f'Dispositivo {dispositivo.nombre_dispositivo} marcado como confiable.')
        return redirect('dispositivos')

    return redirect('dispositivos')

@login_required
def revocar_dispositivo_view(request, dispositivo_id):
    """Vista para revocar un dispositivo confiable"""
    dispositivo = get_object_or_404(
        DispositivoUsuario, 
        id=dispositivo_id, 
        usuario=request.user
    )
    
    if request.method == 'POST':
        dispositivo.activo = False
        dispositivo.es_confiable = False
        dispositivo.save()
        messages.success(request, f'Dispositivo {dispositivo.nombre_dispositivo} revocado correctamente.')
        return redirect('dispositivos')
    
    return render(request, 'Login/revocar_dispositivo.html', {
        'dispositivo': dispositivo
    })

@never_cache
def logout_(request):
    if request.user.is_authenticated:
        request.user.cierre_sesion = timezone.now()
        request.user.save()
    logout(request)
    return redirect('descripcion')

@login_required
def perfil_usuario_view(request):
    return render(request, 'Login/perfil_usuario.html', {
        'usuario': request.user
    })

@login_required
def marcar_principal_view(request, dispositivo_id):
    usuario = request.user
    dispositivo = get_object_or_404(DispositivoUsuario, id=dispositivo_id, usuario=usuario)

    if request.method == 'POST':
        # Desmarcar cualquier dispositivo anterior como principal
        usuario.dispositivos.update(es_principal=False)
        dispositivo.es_principal = True
        dispositivo.es_confiable = True
        dispositivo.save()
        messages.success(request, 'Dispositivo marcado como principal.')
        return redirect('dispositivos')

    return redirect('dispositivos')

@login_required
def cambiar_password_view(request):
    if request.method == 'POST':
        form = CambiarPasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            if user.check_password(form.cleaned_data['password_actual']):
                user.set_password(form.cleaned_data['nueva_password'])
                user.save()
                update_session_auth_hash(request, user)  # Para no cerrar sesión
                messages.success(request, 'Contraseña cambiada correctamente.')
                return redirect('perfil_usuario')
            else:
                form.add_error('password_actual', 'Contraseña actual incorrecta.')
    else:
        form = CambiarPasswordForm()

    return render(request, 'Login/cambiar_password.html', {'form': form})
