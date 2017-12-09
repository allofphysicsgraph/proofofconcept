from models import Derivation
from django import forms


class MyModelForm(forms.ModelForm):
    class Meta:
        model = Derivation
        fields = '__all__'