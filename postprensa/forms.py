from django import forms
from .models import ControlCalidad, ImagenControl, Maquinista, OperarioInspeccion, TipoDefecto, OpcionDefecto
from ordenes_trabajo.models import Cliente

class ControlCalidadForm(forms.ModelForm):
    AUTORIZADORES = [
        ('', '-- Seleccione Autorizador --'),
        ('Garbi Enzo', 'Garbi Enzo'),
        ('Luppo Gaston', 'Luppo Gaston'),
        ('Gonzalez Ana', 'Gonzalez Ana'),
        ('Ridissi Gabriel', 'Ridissi Gabriel'),
    ]
    
    autorizo_envio = forms.ChoiceField(
        choices=AUTORIZADORES, 
        required=False, 
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = ControlCalidad
        fields = [
            'orden', 'operario', 'maquinista', 'cliente', 'bobina', 'cantidad_descartada',
            'defectos', 'opciones_defecto',
            'detalle_defecto', 'llego_cantidad', 'autorizo_envio', 'observaciones'
        ]
        widgets = {
            'detalle_defecto': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Detalle el problema...'}),
            'observaciones': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Notas adicionales...'}),
            'orden': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese N° de Orden'}),
            'operario': forms.Select(attrs={'class': 'form-select'}),
            'maquinista': forms.Select(attrs={'class': 'form-select'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'bobina': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad_descartada': forms.NumberInput(attrs={'class': 'form-control'}),
            'llego_cantidad': forms.CheckboxInput(attrs={'class': 'd-none', 'id': 'id_llego_cantidad'}),
            'defectos': forms.CheckboxSelectMultiple(),
            'opciones_defecto': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['operario'].queryset = OperarioInspeccion.objects.filter(activo=True)
        self.fields['maquinista'].queryset = Maquinista.objects.filter(activo=True)
        self.fields['cliente'].queryset = Cliente.objects.all().order_by('nombre')
        self.fields['defectos'].queryset = TipoDefecto.objects.filter(activo=True)
        self.fields['opciones_defecto'].queryset = OpcionDefecto.objects.filter(activo=True)
        self.fields['operario'].empty_label = "-- Seleccione un operario --"
        self.fields['maquinista'].empty_label = "-- Seleccione un maquinista --"
        self.fields['cliente'].empty_label = "-- Seleccione un cliente --"

class ImagenControlForm(forms.ModelForm):
    class Meta:
        model = ImagenControl
        fields = ['imagen', 'descripcion']

class MaquinistaForm(forms.ModelForm):
    class Meta:
        model = Maquinista
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del maquinista'
            }),
        }

class OperarioInspeccionForm(forms.ModelForm):
    class Meta:
        model = OperarioInspeccion
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del operario'
            }),
        }
