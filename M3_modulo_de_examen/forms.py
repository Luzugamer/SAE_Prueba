from django import forms
from .models import Examen, Pregunta, Opcion, ExamenPregunta

class ExamenForm(forms.ModelForm):
    class Meta:
        model = Examen
        fields = ['titulo', 'descripcion', 'duracion', 'tipo_examen', 'nivel_dificultad']  # AGREGAR nivel_dificultad
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

class PreguntaForm(forms.ModelForm):
    class Meta:
        model = Pregunta
        fields = ['enunciado', 'tipo_pregunta', 'tema', 'respuesta_correcta', 'explicacion']  # QUITAR nivel_dificultad, AGREGAR tema
        widgets = {
            'enunciado': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'explicacion': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'respuesta_correcta': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_pregunta': forms.Select(attrs={'class': 'form-control', 'id': 'id_tipo_pregunta'}),
            'tema': forms.Select(attrs={'class': 'form-control'}),  # AGREGAR
        }

    def __init__(self, *args, curso=None, **kwargs):  # MODIFICAR
        super().__init__(*args, **kwargs)
        self.fields['respuesta_correcta'].required = False
        if curso:  # AGREGAR
            self.fields['tema'].queryset = curso.temas.all()

class OpcionForm(forms.ModelForm):
    class Meta:
        model = Opcion
        fields = ['texto_opcion', 'es_correcta']
        widgets = {
            'texto_opcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Escriba la opción'}),
            'es_correcta': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

OpcionFormSet = forms.inlineformset_factory(
    Pregunta, Opcion, form=OpcionForm, extra=4, max_num=5, can_delete=False
)

class ResponderExamenForm(forms.Form):
    def __init__(self, examen, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for pregunta in examen.examenpregunta_set.all().order_by('orden'):
            field_name = f'pregunta_{pregunta.id}'
            
            if pregunta.pregunta.tipo_pregunta == 'opcion_multiple':
                opciones = pregunta.pregunta.opciones.all()
                choices = [(op.id, op.texto_opcion) for op in opciones]
                self.fields[field_name] = forms.ChoiceField(
                    label=pregunta.pregunta.enunciado,
                    choices=choices,
                    widget=forms.RadioSelect
                )
            elif pregunta.pregunta.tipo_pregunta == 'verdadero_falso':
                self.fields[field_name] = forms.ChoiceField(
                    label=pregunta.pregunta.enunciado,
                    choices=[('True', 'Verdadero'), ('False', 'Falso')],
                    widget=forms.RadioSelect
                )
            else:
                self.fields[field_name] = forms.CharField(
                    label=pregunta.pregunta.enunciado,
                    widget=forms.TextInput
                )