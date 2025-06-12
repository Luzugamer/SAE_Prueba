import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Comunidad, Mensaje, MiembroComunidad, Invitacion, Reporte, Perfil
from django.contrib.auth.models import User
import json

def home(request):
    """Vista principal de bienvenida"""
    comunidades_destacadas = Comunidad.objects.filter(es_destacada=True, activa=True)[:6]
    todas_comunidades = Comunidad.objects.filter(activa=True).order_by('-fecha_creacion')
    
    context = {
        'comunidades_destacadas': comunidades_destacadas,
        'todas_comunidades': todas_comunidades,
    }
    return render(request, "foro/inicio.html", context)
@login_required 
def comunidad(request):
    return render(request, 'foro/comunidad.html')

@login_required
def crear_comunidad(request):
    # Solo profesores pueden crear comunidades
    if not hasattr(request.user, 'perfil') or request.user.perfil.rol != 'profesor':
        messages.error(request, "Solo los profesores pueden crear comunidades.")
        return redirect('foro_inicio')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        institucion_afiliada = request.POST.get('institucion_afiliada', '')
        icono = request.FILES.get('icono')
        
        if nombre and descripcion:
            comunidad = Comunidad.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                institucion_afiliada=institucion_afiliada,
                creador=request.user,
                icono=icono if icono else None
            )
            # Agregar al creador como miembro profesor
            MiembroComunidad.objects.create(
                usuario=request.user,
                comunidad=comunidad,
                rol='profesor'
            )
            messages.success(request, f"Comunidad '{nombre}' creada exitosamente.")
            return redirect('comunidad_detalle', comunidad_id=comunidad.id)
        else:
            messages.error(request, "Por favor completa todos los campos requeridos.")

    return render(request, "foro/crear_comunidad.html")

@login_required
def editar_comunidad(request, comunidad_id):
    comunidad = get_object_or_404(Comunidad, id=comunidad_id)
    
    # Solo el creador puede editar
    if comunidad.creador != request.user:
        messages.error(request, "No tienes permisos para editar esta comunidad.")
        return redirect('comunidad_detalle', comunidad_id=comunidad_id)
    
    if request.method == 'POST':
        comunidad.nombre = request.POST.get('nombre', comunidad.nombre)
        comunidad.descripcion = request.POST.get('descripcion', comunidad.descripcion)
        comunidad.institucion_afiliada = request.POST.get('institucion_afiliada', comunidad.institucion_afiliada)
        
        if request.FILES.get('icono'):
            comunidad.icono = request.FILES.get('icono')
        
        comunidad.save()
        messages.success(request, "Comunidad actualizada exitosamente.")
        return redirect('comunidad_detalle', comunidad_id=comunidad_id)
    
    return render(request, "foro/editar_comunidad.html", {'comunidad': comunidad})

@login_required
def eliminar_comunidad(request, comunidad_id):
    comunidad = get_object_or_404(Comunidad, id=comunidad_id)
    
    if comunidad.creador == request.user:
        comunidad.activa = False
        comunidad.save()
        messages.success(request, "Comunidad eliminada exitosamente.")
    else:
        messages.error(request, "No tienes permisos para eliminar esta comunidad.")
    
    return redirect('comunidades_inicio')

@login_required
def comunidad_detalle(request, comunidad_id):
    comunidad = get_object_or_404(Comunidad, id=comunidad_id, activa=True)
    es_miembro = MiembroComunidad.objects.filter(usuario=request.user, comunidad=comunidad).exists()
    
    if request.method == "POST":
        if es_miembro:
            contenido = request.POST.get("contenido")
            if contenido:
                Mensaje.objects.create(
                    comunidad=comunidad,
                    autor=request.user,
                    contenido=contenido
                )
                messages.success(request, "Mensaje enviado exitosamente.")
                return redirect("comunidad_detalle", comunidad_id=comunidad_id)
        else:
            messages.error(request, "Debes ser miembro de la comunidad para enviar mensajes.")
    
    mensajes = []
    if es_miembro:
        mensajes = Mensaje.objects.filter(comunidad=comunidad).order_by("-timestamp")
        mensajes = [m for m in mensajes if m.es_vigente()]
    
    context = {
        'comunidad': comunidad,
        'mensajes': mensajes,
        'es_miembro': es_miembro,
        'es_creador': comunidad.creador == request.user,
    }
    return render(request, "foro/comunidad_detalle.html", context)

@login_required
def unirse_comunidad(request, comunidad_id):
    comunidad = get_object_or_404(Comunidad, id=comunidad_id, activa=True)
    
    if request.method == 'POST':
        if not MiembroComunidad.objects.filter(usuario=request.user, comunidad=comunidad).exists():
            MiembroComunidad.objects.create(usuario=request.user, comunidad=comunidad)
            messages.success(request, f"Te has unido exitosamente a {comunidad.nombre}.")
        else:
            messages.info(request, "Ya eres miembro de esta comunidad.")
    
    return redirect('comunidad_detalle', comunidad_id=comunidad_id)

@login_required
def salir_comunidad(request, comunidad_id):
    comunidad = get_object_or_404(Comunidad, id=comunidad_id)
    miembro = MiembroComunidad.objects.filter(usuario=request.user, comunidad=comunidad).first()
    
    if miembro:
        miembro.delete()
        messages.success(request, f"Has salido de {comunidad.nombre}.")
    
    return redirect('comunidades_home')

@login_required
def zona_descanso(request, comunidad_id):
    comunidad = get_object_or_404(Comunidad, id=comunidad_id, activa=True)
    
    # Verificar que el usuario sea miembro
    es_miembro = MiembroComunidad.objects.filter(usuario=request.user, comunidad=comunidad).exists()
    if not es_miembro:
        messages.error(request, "Debes ser miembro de la comunidad para acceder a la zona de descanso.")
        return redirect('comunidad_detalle', comunidad_id=comunidad_id)
    
    miembros_activos = comunidad.get_miembros_activos()
    miembros_inactivos = comunidad.get_miembros_inactivos()
    
    context = {
        'comunidad': comunidad,
        'miembros_activos': miembros_activos,
        'miembros_inactivos': miembros_inactivos,
        'es_creador': comunidad.creador == request.user,
    }
    return render(request, "foro/zona_descanso.html", context)

@login_required
def buscar_comunidades(request):
    query = request.GET.get("q", "")
    resultados = []
    
    if query:
        resultados = Comunidad.objects.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query),
            activa=True
        ).order_by('-es_destacada', '-fecha_creacion')
    
    return render(request, "foro/busqueda.html", {
        "resultados": resultados,
        "query": query
    })

@login_required
def unirse_por_invitacion(request, codigo_invitacion):
    comunidad = get_object_or_404(Comunidad, codigo_invitacion=codigo_invitacion, activa=True)
    
    if not MiembroComunidad.objects.filter(usuario=request.user, comunidad=comunidad).exists():
        MiembroComunidad.objects.create(usuario=request.user, comunidad=comunidad)
        messages.success(request, f"Te has unido exitosamente a {comunidad.nombre} por invitación.")
    else:
        messages.info(request, "Ya eres miembro de esta comunidad.")
    
    return redirect('comunidad_detalle', comunidad_id=comunidad.id)

@login_required
def reportar_comunidad(request, comunidad_id):
    comunidad = get_object_or_404(Comunidad, id=comunidad_id)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo')
        descripcion = request.POST.get('descripcion')
        
        if motivo and descripcion:
            Reporte.objects.create(
                comunidad=comunidad,
                reportado_por=request.user,
                motivo=motivo,
                descripcion=descripcion
            )
            messages.success(request, "Reporte enviado exitosamente.")
        else:
            messages.error(request, "Por favor completa todos los campos.")
        
        return redirect('zona_descanso', comunidad_id=comunidad_id)
    
    return render(request, "foro/reportar.html", {'comunidad': comunidad})

@login_required
def asistente_ia(request):
    if request.method == 'POST':
        pregunta = request.POST.get('pregunta', '').strip()
        try:
            response = requests.post(
                "http://localhost:8001/api/responder",
                json={"pregunta": pregunta},
                timeout=10
            )
            respuesta = response.json().get("respuesta", "No se recibió respuesta.")
        except Exception as e:
            respuesta = "Ocurrió un error al conectar con la API externa."

        return JsonResponse({'respuesta': respuesta})
    return render(request, "foro/asistente_ia.html")

@login_required
def principio(request):
    return render(request, 'foro/principio.html')

@login_required
def mis_comunidades(request):
    """Vista para mostrar las comunidades del usuario"""
    mis_comunidades = Comunidad.objects.filter(
        miembros=request.user,
        activa=True
    ).order_by('-fecha_creacion')
    
    return render(request, "foro/mis_comunidades.html", {
        'comunidades': mis_comunidades
    })
from django.shortcuts import redirect

@login_required
def crear_comunidad(request):
    """
    Vista para crear una nueva comunidad educativa.
    Solo los profesores pueden crear comunidades.
    """
    
    # Verificar que el usuario tenga perfil y sea profesor
    if request.method == 'POST':
        try:
            # Obtener y validar datos del formulario
            nombre = request.POST.get('nombre', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            institucion_afiliada = request.POST.get('institucion_afiliada', '').strip()
            icono = request.FILES.get('icono')
            
            # Validaciones básicas
            if not nombre:
                messages.error(request, "❌ El nombre de la comunidad es obligatorio.")
                return render(request, "foro/crear_comunidad.html")
            
            if len(nombre) < 3:
                messages.error(request, "❌ El nombre debe tener al menos 3 caracteres.")
                return render(request, "foro/crear_comunidad.html")
            
            if len(nombre) > 100:
                messages.error(request, "❌ El nombre no puede exceder los 100 caracteres.")
                return render(request, "foro/crear_comunidad.html")
            
            if not descripcion:
                messages.error(request, "❌ La descripción de la comunidad es obligatoria.")
                return render(request, "foro/crear_comunidad.html")
            
            if len(descripcion) < 10:
                messages.error(request, "❌ La descripción debe tener al menos 10 caracteres.")
                return render(request, "foro/crear_comunidad.html")
            
            # Verificar que no exista una comunidad con el mismo nombre del mismo profesor
            if Comunidad.objects.filter(nombre__iexact=nombre, creador=request.user, activa=True).exists():
                messages.error(request, "❌ Ya tienes una comunidad activa con este nombre.")
                return render(request, "foro/crear_comunidad.html")
            
            # Validar ícono si se proporciona
            if icono:
                # Verificar tamaño del archivo (máximo 5MB)
                if icono.size > 5 * 1024 * 1024:
                    messages.error(request, "❌ El ícono no puede ser mayor a 5MB.")
                    return render(request, "foro/crear_comunidad.html")
                
                # Verificar tipo de archivo
                allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
                if icono.content_type not in allowed_types:
                    messages.error(request, "❌ El ícono debe ser una imagen (JPG, PNG, GIF o WebP).")
                    return render(request, "foro/crear_comunidad.html")
            
            # Crear la comunidad
            nueva_comunidad = Comunidad.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                institucion_afiliada=institucion_afiliada if institucion_afiliada else None,
                creador=request.user,
                icono=icono if icono else None,
                puntos_prestigio=0,
                es_destacada=False,
                activa=True
            )
            
            # Agregar al creador como primer miembro con rol de profesor
            MiembroComunidad.objects.create(
                usuario=request.user,
                comunidad=nueva_comunidad,
                rol='profesor',
                estado='activo'
            )
            
            # Crear mensaje de bienvenida automático
            mensaje_bienvenida = f"""
            🎉 ¡Bienvenidos a {nombre}! 
            
            Esta comunidad ha sido creada para fomentar el aprendizaje colaborativo y la participación activa.
            
            📋 Información importante:
            • Mantén un ambiente respetuoso y constructivo
            • Participa activamente en las discusiones
            • Comparte tus conocimientos con otros miembros
            
            ¡Esperamos que disfrutes esta experiencia de aprendizaje!
            
            - {request.user.get_full_name() or request.user.username}
            """.strip()
            
            Mensaje.objects.create(
                comunidad=nueva_comunidad,
                autor=request.user,
                contenido=mensaje_bienvenida,
                es_importante=True
            )
            
            # Mensaje de éxito
            messages.success(
                request, 
                f"🎉 ¡Comunidad '{nombre}' creada exitosamente! "
                f"Código de invitación: {nueva_comunidad.codigo_invitacion}"
            )
            
            # Log de la acción (opcional, para auditoría)
            import logging
            logger = logging.getLogger('comunidades')
            logger.info(
                f"Nueva comunidad creada: {nombre} (ID: {nueva_comunidad.id}) "
                f"por {request.user.username} (ID: {request.user.id})"
            )
            
            # Redirigir a la página de detalle de la comunidad creada
            return redirect('comunidad:comunidad_detalle', comunidad_id=nueva_comunidad.id)
            
        except Exception as e:
            # Manejar errores inesperados
            import logging
            logger = logging.getLogger('comunidades')
            logger.error(f"Error al crear comunidad: {str(e)} - Usuario: {request.user.username}")
            
            messages.error(
                request, 
                "❌ Ocurrió un error inesperado al crear la comunidad. "
                "Por favor, inténtalo nuevamente."
            )
            return render(request, "foro/crear_comunidad.html")
    
    # Si es GET, mostrar el formulario
    else:
        # Obtener estadísticas para mostrar en la página
        total_comunidades = Comunidad.objects.filter(activa=True).count()
        mis_comunidades = Comunidad.objects.filter(creador=request.user, activa=True).count()
        
        # Verificar límite de comunidades por profesor (opcional)
        limite_comunidades = 10  # Puedes configurar esto en settings.py
        if mis_comunidades >= limite_comunidades:
            messages.warning(
                request, 
                f"⚠️ Has alcanzado el límite máximo de {limite_comunidades} comunidades activas."
            )
        
        context = {
            'total_comunidades': total_comunidades,
            'mis_comunidades': mis_comunidades,
            'limite_comunidades': limite_comunidades,
            'puede_crear': mis_comunidades < limite_comunidades,
        }
        
        return render(request, "foro/crear_comunidad.html")

@login_required
def verificar_nombre_comunidad(request):
    if request.method == "POST":
        nombre = request.POST.get('nombre', '')
        existe = Comunidad.objects.filter(nombre=nombre).exists()
        return JsonResponse({'disponible': not existe})
    return JsonResponse({'error': 'Método no permitido'}, status=405)
    
@login_required
def invitar_estudiantes(request, comunidad_id):
    """Vista para invitar estudiantes a la comunidad"""
    comunidad = get_object_or_404(Comunidad, id=comunidad_id, activa=True)
    
    # Solo miembros pueden invitar
    es_miembro = MiembroComunidad.objects.filter(usuario=request.user, comunidad=comunidad).exists()
    if not es_miembro:
        messages.error(request, "No tienes permisos para invitar a esta comunidad.")
        return redirect('comunidad_detalle', comunidad_id=comunidad_id)
    
    if request.method == 'POST':
        email_o_username = request.POST.get('email_o_username')
        try:
            # Buscar por email o username
            usuario_invitado = User.objects.filter(
                Q(email=email_o_username) | Q(username=email_o_username)
            ).first()
            
            if usuario_invitado:
                # Verificar que no sea ya miembro
                if not MiembroComunidad.objects.filter(usuario=usuario_invitado, comunidad=comunidad).exists():
                    # Crear invitación
                    invitacion, created = Invitacion.objects.get_or_create(
                        comunidad=comunidad,
                        invitado=usuario_invitado,
                        defaults={'invitado_por': request.user}
                    )
                    if created:
                        messages.success(request, f"Invitación enviada a {usuario_invitado.username}")
                    else:
                        messages.info(request, "Ya existe una invitación pendiente para este usuario")
                else:
                    messages.info(request, "Este usuario ya es miembro de la comunidad")
            else:
                messages.error(request, "Usuario no encontrado")
        except Exception as e:
            messages.error(request, "Error al enviar la invitación")
    
    return render(request, "foro/invitar_estudiantes.html", {'comunidad': comunidad})

@login_required
def gestionar_miembros(request, comunidad_id):
    """Vista para gestionar miembros de la comunidad"""
    comunidad = get_object_or_404(Comunidad, id=comunidad_id, activa=True)
    
    # Solo el creador puede gestionar miembros
    if comunidad.creador != request.user:
        messages.error(request, "No tienes permisos para gestionar esta comunidad.")
        return redirect('comunidad_detalle', comunidad_id=comunidad_id)
    
    miembros = MiembroComunidad.objects.filter(comunidad=comunidad)
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        miembro_id = request.POST.get('miembro_id')
        
        try:
            miembro = MiembroComunidad.objects.get(id=miembro_id, comunidad=comunidad)
            
            if accion == 'cambiar_estado':
                miembro.estado = 'inactivo' if miembro.estado == 'activo' else 'activo'
                miembro.save()
                messages.success(request, f"Estado de {miembro.usuario.username} actualizado")
            elif accion == 'cambiar_rol':
                miembro.rol = 'profesor' if miembro.rol == 'estudiante' else 'estudiante'
                miembro.save()
                messages.success(request, f"Rol de {miembro.usuario.username} actualizado")
            elif accion == 'expulsar':
                if miembro.usuario != request.user:  # No puede expulsarse a sí mismo
                    miembro.delete()
                    messages.success(request, f"{miembro.usuario.username} ha sido expulsado de la comunidad")
                    
        except MiembroComunidad.DoesNotExist:
            messages.error(request, "Miembro no encontrado")
    
    return render(request, "foro/gestionar_miembros.html", {
        'comunidad': comunidad,
        'miembros': miembros
    })

@login_required
def compartir_comunidad(request, comunidad_id):
    """Vista para compartir el código de invitación de la comunidad"""
    comunidad = get_object_or_404(Comunidad, id=comunidad_id, activa=True)
    
    # Solo miembros pueden ver el código
    es_miembro = MiembroComunidad.objects.filter(usuario=request.user, comunidad=comunidad).exists()
    if not es_miembro:
        messages.error(request, "No tienes permisos para acceder a esta información.")
        return redirect('comunidad_detalle', comunidad_id=comunidad_id)
    
    # Generar URL de invitación
    url_invitacion = request.build_absolute_uri(
        f"/comunidad/invitacion/{comunidad.codigo_invitacion}/"
    )
    
    return render(request, "foro/compartir_comunidad.html", {
        'comunidad': comunidad,
        'url_invitacion': url_invitacion
    })