from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Login.decorators import rol_requerido


def pag_descripcion(request):
    return render(request, 'Pages/pag_descripcion.html')

@login_required
def pag_principal(request):
    return render(request, 'Pages/pag_principal.html')

@login_required
def repositorio(request):
    return render(request, 'Pages/repositorio.html')

@login_required
@rol_requerido('estudiante')
def pag_estu(request):
    return render(request, 'Pages/pag_principal.html')

@login_required
@rol_requerido('profesor')
def pag_profe(request):
    return render(request, 'Pages/pag_principal.html')



