from django.forms import ModelForm
from main.models import *


class InferenceRuleForm(ModelForm):
    class Meta:
        model = InferenceRule
        fields = [x.name for x in InferenceRule._meta.get_fields()]