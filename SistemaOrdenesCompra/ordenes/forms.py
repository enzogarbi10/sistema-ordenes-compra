from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from .models import OrdenCompra, ItemOrden, Cliente

class RegistroUsuarioForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Cliente'}),
        }

class OrdenCompraForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and not (user.is_superuser or user.is_staff):
            try:
                self.fields['cliente'].queryset = Cliente.objects.filter(user=user)
                # Auto-select if only one option (which should be the case)
                if self.fields['cliente'].queryset.count() == 1:
                    self.fields['cliente'].initial = self.fields['cliente'].queryset.first()
            except Cliente.DoesNotExist:
                self.fields['cliente'].queryset = Cliente.objects.none()

    class Meta:
        model = OrdenCompra
        fields = ['cliente']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
        }

class ItemOrdenForm(forms.ModelForm):
    class Meta:
        model = ItemOrden
        fields = ['marca', 'elemento', 'cantidad', 'ancho', 'alto', 'forma', 'papel', 'variedad', 
                  'archivo_muestra', 'grado_alcoholico', 'codigo_cliente', 'anio', 'contenido_neto',
                  'serigrafia', 'stamping', 'relieve', 'bajo_relieve', 'gofrado']
        widgets = {
            'marca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Marca'}),
            'elemento': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cant.'}),
            'ancho': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ancho', 'step': '0.01'}),
            'alto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Alto', 'step': '0.01'}),
            'forma': forms.Select(attrs={'class': 'form-select'}),
            'papel': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Papel'}),
            'variedad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Variedad'}),
            'archivo_muestra': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'grado_alcoholico': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Grado Alc.'}),
            'codigo_cliente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cód. Cliente'}),
            'anio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Año'}),
            'contenido_neto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cont. Neto'}),
            'serigrafia': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'stamping': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'relieve': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'bajo_relieve': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gofrado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

ItemOrdenFormSet = inlineformset_factory(
    OrdenCompra, ItemOrden, form=ItemOrdenForm,
    extra=1, can_delete=True
)

from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm

class CustomUserCreationForm(UserCreationForm):
    is_staff = forms.BooleanField(required=False, label="Es Administrador")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'is_staff')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = self.cleaned_data['is_staff']
        if commit:
            user.save()
        return user

class AdminPasswordChangeForm(SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class UserUpdateForm(forms.ModelForm):
    is_staff = forms.BooleanField(required=False, label="Es Administrador")

    class Meta:
        model = User
        fields = ['username', 'email', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['is_staff'].initial = self.instance.is_staff
