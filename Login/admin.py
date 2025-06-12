from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Rol, UsuarioRol

class UsuarioRolInline(admin.TabularInline):
    model = UsuarioRol
    extra = 1

class UsuarioAdmin(BaseUserAdmin):
    # Campos que se mostrarán en la lista de usuarios
    list_display = ('correo_electronico', 'nombre', 'apellido', 'is_active', 'is_staff', 'fecha_registro')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'fecha_registro')
    
    # Campos para búsqueda
    search_fields = ('correo_electronico', 'nombre', 'apellido')
    
    # Organización de campos en el formulario de edición
    fieldsets = (
        (None, {'fields': ('correo_electronico', 'password')}),
        ('Información Personal', {'fields': ('nombre', 'apellido')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'fecha_registro', 'ultima_sesion', 'cierre_sesion')}),
    )
    
    # Campos para el formulario de creación de usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('correo_electronico', 'nombre', 'apellido', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ('fecha_registro', 'last_login', 'ultima_sesion', 'cierre_sesion')
    
    # Campo de ordenamiento
    ordering = ('correo_electronico',)
    
    # Incluir roles inline
    inlines = [UsuarioRolInline]

class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre_rol', 'descripcion')
    search_fields = ('nombre_rol',)

class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol')
    list_filter = ('rol',)
    search_fields = ('usuario__correo_electronico', 'usuario__nombre', 'rol__nombre_rol')

# Registrar los modelos
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Rol, RolAdmin)
admin.site.register(UsuarioRol, UsuarioRolAdmin)

# Personalizar el sitio de administración
admin.site.site_header = "Administración SAE"
admin.site.site_title = "SAE Admin"
admin.site.index_title = "Panel de Administración"