from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from Login.decorators import rol_requerido
from django.contrib import messages
from django.http import JsonResponse
from .models import Curso, Examen, Pregunta, Opcion, ExamenPregunta, RespuestaUsuario, ResultadoExamen
from .forms import ExamenForm, PreguntaForm, OpcionFormSet, ResponderExamenForm

@login_required
def lista_examenes_curso(request, curso_codigo):
    curso = get_object_or_404(Curso, codigo=curso_codigo)
    examenes = Examen.objects.filter(curso=curso, activo=True)
    
    # Verificar si el usuario es profesor para mostrar opciones adicionales
    es_profesor = request.user.usuariorol_set.filter(rol__nombre_rol='profesor').exists()
    
    context = {
        'curso': curso,
        'examenes': examenes,
        'es_profesor': es_profesor,
    }
    return render(request, 'M3_modulo_de_examen/lista_examenes.html', context)

@login_required
@rol_requerido('profesor')
def crear_examen(request, curso_codigo):
    curso = get_object_or_404(Curso, codigo=curso_codigo)
    
    if request.method == 'POST':
        form = ExamenForm(request.POST)
        if form.is_valid():
            examen = form.save(commit=False)
            examen.curso = curso
            examen.creado_por = request.user
            examen.save()
            messages.success(request, 'Examen creado exitosamente!')
            return redirect('agregar_preguntas', examen_id=examen.id)
    else:
        form = ExamenForm()
    
    context = {
        'curso': curso,
        'form': form,
    }
    return render(request, 'M3_modulo_de_examen/crear_examen.html', context)

@login_required
@rol_requerido('profesor')
def agregar_preguntas(request, examen_id):
    examen = get_object_or_404(Examen, id=examen_id)
    
    if request.method == 'POST':
        pregunta_form = PreguntaForm(request.POST, curso=examen.curso)
        opcion_formset = OpcionFormSet(request.POST, prefix='opciones')
        
        if pregunta_form.is_valid():
            # Guardar la pregunta primero
            pregunta = pregunta_form.save(commit=False)
            pregunta.curso = examen.curso
            pregunta.creada_por = request.user
            pregunta.save()
            
            # Manejar diferentes tipos de pregunta
            if pregunta.tipo_pregunta == 'opcion_multiple':
                if opcion_formset.is_valid():
                    opciones = opcion_formset.save(commit=False)
                    opciones_validas = []
                    for opcion in opciones:
                        if opcion.texto_opcion.strip():  # Solo guardar opciones con texto
                            opcion.pregunta = pregunta
                            opciones_validas.append(opcion)
                    
                    if opciones_validas:
                        Opcion.objects.bulk_create(opciones_validas)
                    else:
                        pregunta.delete()
                        messages.error(request, 'Debe agregar al menos una opción válida.')
                        return redirect('agregar_preguntas', examen_id=examen.id)
                else:
                    pregunta.delete()
                    messages.error(request, 'Error en las opciones de la pregunta.')
                    return redirect('agregar_preguntas', examen_id=examen.id)
                    
            elif pregunta.tipo_pregunta == 'verdadero_falso':
                # Crear automáticamente las opciones Verdadero y Falso
                opcion_verdadero = Opcion.objects.create(
                    pregunta=pregunta,
                    texto_opcion='Verdadero',
                    es_correcta=(pregunta.respuesta_correcta.lower() in ['verdadero', 'true', 'v', '1'])
                )
                opcion_falso = Opcion.objects.create(
                    pregunta=pregunta,
                    texto_opcion='Falso',
                    es_correcta=(pregunta.respuesta_correcta.lower() in ['falso', 'false', 'f', '0'])
                )
            
            # Para respuesta_corta no necesitamos crear opciones
            
            # Asociar la pregunta al examen
            orden = ExamenPregunta.objects.filter(examen=examen).count() + 1
            ExamenPregunta.objects.create(examen=examen, pregunta=pregunta, orden=orden)
            
            messages.success(request, 'Pregunta agregada al examen exitosamente!')
            return redirect('agregar_preguntas', examen_id=examen.id)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        pregunta_form = PreguntaForm(curso=examen.curso)
        opcion_formset = OpcionFormSet(queryset=Opcion.objects.none(), prefix='opciones')
    
    preguntas_examen = examen.examenpregunta_set.all().order_by('orden')
    
    context = {
        'examen': examen,
        'pregunta_form': pregunta_form,
        'opcion_formset': opcion_formset,
        'preguntas_examen': preguntas_examen,
    }
    return render(request, 'M3_modulo_de_examen/agregar_preguntas.html', context)

@login_required
@rol_requerido('profesor')
def eliminar_examen(request, examen_id):
    examen = get_object_or_404(Examen, id=examen_id)
    curso_codigo = examen.curso.codigo
    
    if request.method == 'POST':
        examen.delete()
        messages.success(request, 'Examen eliminado exitosamente!')
        return redirect('lista_examenes_curso', curso_codigo=curso_codigo)
    
    context = {
        'examen': examen,
    }
    return render(request, 'M3_modulo_de_examen/confirmar_eliminar.html', context)

@login_required
def responder_examen(request, examen_id):
    examen = get_object_or_404(Examen, id=examen_id, activo=True)
    
    # Verificar si el usuario ya completó este examen
    if ResultadoExamen.objects.filter(usuario=request.user, examen=examen).exists():
        messages.warning(request, 'Ya has completado este examen.')
        return redirect('resultado_examen', examen_id=examen.id)
    
    preguntas = examen.examenpregunta_set.all().order_by('orden')
    
    if request.method == 'POST':
        form = ResponderExamenForm(examen, request.POST)
        if form.is_valid():
            respuestas = []
            correctas = 0
            
            for pregunta in preguntas:
                respuesta = form.cleaned_data.get(f'pregunta_{pregunta.id}')
                es_correcta = False
                opcion_seleccionada = None
                
                if pregunta.pregunta.tipo_pregunta == 'opcion_multiple':
                    try:
                        opcion_seleccionada = Opcion.objects.get(id=respuesta)
                        es_correcta = opcion_seleccionada.es_correcta
                        respuesta_texto = opcion_seleccionada.texto_opcion
                    except (Opcion.DoesNotExist, ValueError):
                        es_correcta = False
                        respuesta_texto = "Sin respuesta"
                elif pregunta.pregunta.tipo_pregunta == 'verdadero_falso':
                    # Para verdadero/falso, buscar la opción correspondiente
                    opcion_seleccionada = pregunta.pregunta.opciones.get(
                        texto_opcion='Verdadero' if respuesta == 'True' else 'Falso'
                    )
                    es_correcta = opcion_seleccionada.es_correcta
                    respuesta_texto = opcion_seleccionada.texto_opcion
                else:  # respuesta_corta
                    respuesta_texto = respuesta
                    es_correcta = (respuesta.strip().lower() == pregunta.pregunta.respuesta_correcta.strip().lower())
                
                respuestas.append(RespuestaUsuario(
                    usuario=request.user,
                    examen_pregunta=pregunta,
                    respuesta=respuesta_texto,
                    opcion_seleccionada=opcion_seleccionada,
                    correcta=es_correcta
                ))
                
                if es_correcta:
                    correctas += 1
            
            # Guardar todas las respuestas
            RespuestaUsuario.objects.bulk_create(respuestas)
            
            # Calcular puntaje
            puntaje = (correctas / preguntas.count()) * 100 if preguntas.count() > 0 else 0
            
            # Guardar resultado
            ResultadoExamen.objects.create(
                usuario=request.user,
                examen=examen,
                puntaje=puntaje,
                tiempo_empleado=0  # Implementar lógica de tiempo
            )
            
            messages.success(request, f'Examen completado! Puntaje: {puntaje:.2f}%')
            return redirect('resultado_examen', examen_id=examen.id)
    else:
        form = ResponderExamenForm(examen)
    
    context = {
        'examen': examen,
        'preguntas': preguntas,
        'form': form,
    }
    return render(request, 'M3_modulo_de_examen/responder_examen.html', context)

@login_required
def resultado_examen(request, examen_id):
    examen = get_object_or_404(Examen, id=examen_id)
    resultado = get_object_or_404(ResultadoExamen, examen=examen, usuario=request.user)
    respuestas = RespuestaUsuario.objects.filter(examen_pregunta__examen=examen, usuario=request.user)
    
    context = {
        'examen': examen,
        'resultado': resultado,
        'respuestas': respuestas,
    }
    return render(request, 'M3_modulo_de_examen/resultado_examen.html', context)

@login_required
@rol_requerido('profesor')
def estadisticas_examen(request, examen_id):
    examen = get_object_or_404(Examen, id=examen_id)
    resultados = examen.resultados.all()  # Usando related_name
    
    context = {
        'examen': examen,
        'promedio': examen.promedio_puntaje,  # Usando property
        'intentos': resultados.count(),
        'resultados': resultados,
    }
    return render(request, 'M3_modulo_de_examen/estadisticas_examen.html', context)