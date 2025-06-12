from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps

@receiver(post_migrate)
def crear_cursos_iniciales(sender, **kwargs):
    """
    Signal que se ejecuta después de las migraciones para crear cursos básicos
    """
    # Solo ejecutar para nuestra app específica
    if sender.name != 'M3_modulo_de_examen':  # Cambia por el nombre real de tu app
        return
    
    # Obtener el modelo Curso
    Curso = apps.get_model('M3_modulo_de_examen', 'Curso')
    
    # Lista de cursos básicos que queremos crear
    cursos_iniciales = [
        {
            'nombre': 'Física',
            'codigo': 'fisica',
            'descripcion': 'Curso de Física - Mecánica, Termodinámica, Electromagnetismo'
        },
        {
            'nombre': 'Geometría',
            'codigo': 'geometria',
            'descripcion': 'Curso de Geometría - Plana y del Espacio'
        },
        {
            'nombre': 'Álgebra',
            'codigo': 'algebra',
            'descripcion': 'Curso de Álgebra - Ecuaciones, Funciones y Sistemas'
        },
        {
            'nombre': 'Química',
            'codigo': 'quimica',
            'descripcion': 'Curso de Química - Orgánica, Inorgánica y Analítica'
        },
        {
            'nombre': 'Biología',
            'codigo': 'biologia',
            'descripcion': 'Curso de Biología - Celular, Molecular y Ecosistemas'
        },
        {
            'nombre': 'Historia',
            'codigo': 'historia',
            'descripcion': 'Curso de Historia - Universal y Nacional'
        },
        {
            'nombre': 'Literatura',
            'codigo': 'literatura',
            'descripcion': 'Curso de Literatura - Clásica y Contemporánea'
        },
        {
            'nombre': 'Geografía',
            'codigo': 'geografia',
            'descripcion': 'Curso de Geografía - Física y Humana'
        }
    ]
    
    # Crear cursos que no existan
    cursos_creados = 0
    for curso_data in cursos_iniciales:
        curso, created = Curso.objects.get_or_create(
            codigo=curso_data['codigo'],
            defaults={
                'nombre': curso_data['nombre'],
                'descripcion': curso_data['descripcion']
            }
        )
        if created:
            cursos_creados += 1
            print(f"✓ Curso creado: {curso.nombre}")
    
    if cursos_creados > 0:
        print(f"🎉 Se crearon {cursos_creados} cursos automáticamente")
    else:
        print("ℹ️ Todos los cursos ya existían en la base de datos")