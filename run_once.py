import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SAE.settings')
django.setup()

from Login.models import Usuario  # ajusta si tu modelo está en otro lugar

# Ejecutar migraciones primero
os.system("python manage.py migrate")

# Datos del superusuario
correo = "lp962708128@gmail.com"
nombre = "Admin"
apellido = "Admin"
password = "Adminperuano123"

# Crear superusuario si no existe
if not Usuario.objects.filter(correo_electronico=correo).exists():
    Usuario.objects.create_superuser(
        correo_electronico=correo,
        nombre=nombre,
        apellido=apellido,
        password=password
    )
    print("✅ Superusuario creado correctamente")
else:
    print("ℹ️ Ya existe un superusuario con ese correo")
