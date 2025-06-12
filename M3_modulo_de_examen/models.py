from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Curso(models.Model):
    nombre = models.CharField(max_length=50)
    codigo = models.CharField(max_length=10, unique=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ['nombre']
        # Asegurar que el nombre de la tabla sea consistente
        db_table = 'M3_modulo_de_examen_curso'
    
    def __str__(self):
        return self.nombre

class Examen(models.Model):
    TIPO_EXAMEN_CHOICES = [
        ('simulacro', 'Simulacro'),
        ('simulacroFlash', 'SimulacroFlash')
    ]
    
    NIVEL_DIFICULTAD_CHOICES = [
        ('facil', 'Fácil'),
        ('medio', 'Medio'),
        ('dificil', 'Difícil'),
    ]
    
    nivel_dificultad = models.CharField(max_length=10, choices=NIVEL_DIFICULTAD_CHOICES, default='medio')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='examenes')
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    duracion = models.PositiveIntegerField(
        help_text="Duración en minutos",
        validators=[MinValueValidator(1), MaxValueValidator(300)]
    )
    tipo_examen = models.CharField(max_length=20, choices=TIPO_EXAMEN_CHOICES)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='examenes_creados')
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Examen"
        verbose_name_plural = "Exámenes"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.titulo} - {self.curso.nombre}"
    
    @property
    def numero_preguntas(self):
        return self.examenpregunta_set.count()
    
    @property
    def promedio_puntaje(self):
        resultados = self.resultados.all()  # Usando related_name
        if resultados.exists():
            return resultados.aggregate(models.Avg('puntaje'))['puntaje__avg']
        return 0

class Tema(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='temas')
    
    class Meta:
        verbose_name = "Tema"
        verbose_name_plural = "Temas"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Pregunta(models.Model):
    TIPO_PREGUNTA_CHOICES = [
        ('opcion_multiple', 'Opción Múltiple'),
        ('verdadero_falso', 'Verdadero/Falso'),
        ('respuesta_corta', 'Respuesta Corta'),
    ]
    
    NIVEL_DIFICULTAD_CHOICES = [
        ('facil', 'Fácil'),
        ('medio', 'Medio'),
        ('dificil', 'Difícil'),
    ]

    tema = models.ForeignKey(Tema, on_delete=models.SET_NULL, null=True, blank=True, related_name='preguntas')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='preguntas')
    enunciado = models.TextField()
    tipo_pregunta = models.CharField(max_length=20, choices=TIPO_PREGUNTA_CHOICES)
    respuesta_correcta = models.TextField(blank=True, null=True)
    explicacion = models.TextField(blank=True)
    creada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preguntas_creadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Pregunta"
        verbose_name_plural = "Preguntas"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.enunciado[:50]}..." if len(self.enunciado) > 50 else self.enunciado
    
    def clean(self):
        from django.core.exceptions import ValidationError
        pass

class Opcion(models.Model):
    pregunta = models.ForeignKey(Pregunta, related_name='opciones', on_delete=models.CASCADE)
    texto_opcion = models.TextField()
    es_correcta = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Opción"
        verbose_name_plural = "Opciones"
    
    def __str__(self):
        return f"{self.texto_opcion[:20]}... (Correcta: {self.es_correcta})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.pregunta.tipo_pregunta != 'opcion_multiple':
            raise ValidationError('Las opciones solo pueden existir para preguntas de opción múltiple.')

class ExamenPregunta(models.Model):
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    orden = models.PositiveIntegerField()
    
    class Meta:
        verbose_name = "Pregunta del Examen"
        verbose_name_plural = "Preguntas del Examen"
        ordering = ['orden']
        unique_together = ['examen', 'pregunta']
    
    def __str__(self):
        return f"{self.examen.titulo} - Pregunta {self.orden}"

class RespuestaUsuario(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='respuestas')
    examen_pregunta = models.ForeignKey(ExamenPregunta, on_delete=models.CASCADE)
    respuesta = models.TextField(blank=True, null=True)
    opcion_seleccionada = models.ForeignKey(Opcion, on_delete=models.SET_NULL, null=True, blank=True)
    correcta = models.BooleanField(default=False)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Respuesta del Usuario"
        verbose_name_plural = "Respuestas de los Usuarios"
        unique_together = ['usuario', 'examen_pregunta']
        ordering = ['-fecha_respuesta']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.examen_pregunta}"

class ResultadoExamen(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resultados_examenes')
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE, related_name='resultados')
    puntaje = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    fecha_realizacion = models.DateTimeField(auto_now_add=True)
    tiempo_empleado = models.PositiveIntegerField(
        help_text="Tiempo empleado en segundos",
        validators=[MinValueValidator(1)]
    )
    
    class Meta:
        verbose_name = "Resultado del Examen"
        verbose_name_plural = "Resultados de los Exámenes"
        ordering = ['-fecha_realizacion']
        unique_together = ['usuario', 'examen']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.examen.titulo} - {self.puntaje}%"
    
    @property
    def tiempo_empleado_formateado(self):
        """Devuelve el tiempo empleado en formato MM:SS"""
        minutos = self.tiempo_empleado // 60
        segundos = self.tiempo_empleado % 60
        return f"{minutos:02d}:{segundos:02d}"
    
    @property
    def estado_aprobacion(self):
        """Determina si el examen fue aprobado (>= 70%)"""
        return "Aprobado" if self.puntaje >= 70 else "Reprobado"

class EstadisticaExamen(models.Model):
    TIPO_ESTADISTICA_CHOICES = [
        ('promedio', 'Promedio de Puntajes'),
        ('intentos', 'Número de Intentos'),
        ('dificultad', 'Índice de Dificultad'),
    ]
    
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE, related_name='estadisticas')
    tipo_estadistica = models.CharField(max_length=20, choices=TIPO_ESTADISTICA_CHOICES)
    valor = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Estadística del Examen"
        verbose_name_plural = "Estadísticas de los Exámenes"
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.examen.titulo} - {self.tipo_estadistica}: {self.valor}"