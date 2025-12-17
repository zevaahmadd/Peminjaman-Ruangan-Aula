from django import forms
from .models import Peminjaman
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class PeminjamanForm(forms.ModelForm):
    # 👉 definisikan ulang sebagai DateTimeField, dengan format yang cocok ke flatpickr
    tanggal_mulai = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.TextInput(attrs={
            'class': 'form-control datetimepicker',
            'placeholder': 'hh/bb/tttt jj:mm (WITA)',
            'autocomplete': 'off',
        })
    )

    tanggal_selesai = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.TextInput(attrs={
            'class': 'form-control datetimepicker',
            'placeholder': 'hh/bb/tttt jj:mm (WITA)',
            'autocomplete': 'off',
        })
    )

    class Meta:
        model = Peminjaman
        fields = [
            'ruangan',
            'tanggal_mulai',
            'tanggal_selesai',
            'nama_kegiatan',
            'penanggung_jawab',
            'no_hp_penanggung',
            'keterangan',
        ]
        widgets = {
            'ruangan': forms.Select(attrs={'class': 'form-select'}),
            'nama_kegiatan': forms.TextInput(attrs={'class': 'form-control'}),
            'penanggung_jawab': forms.TextInput(attrs={'class': 'form-control'}),
            'no_hp_penanggung': forms.TextInput(attrs={'class': 'form-control'}),
            'keterangan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
