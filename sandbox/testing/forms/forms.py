from django.forms import ModelForm
from main.models import *


class InferenceRuleForm(ModelForm):
    class Meta:
        model = InferenceRule
        fields = [x.name for x in InferenceRule._meta.get_fields()]


class FeedForm(ModelForm):
    class Meta:
        model = Feed
        fields = [x.name for x in Feed._meta.get_fields()]


class ExpressionForm(ModelForm):
    class Meta:
        model = Expression
        fields = [x.name for x in Expression._meta.get_fields()]


class ConnectionForm(ModelForm):
    class Meta:
        model = Connection
        fields = [x.name for x in Connection._meta.get_fields()]


class SymbolForm(ModelForm):
    class Meta:
        model = Symbol
        fields = [x.name for x in Symbol._meta.get_fields()]
