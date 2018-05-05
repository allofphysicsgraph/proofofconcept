# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from main.forms import InferenceRuleForm


def NewInferenceRule(request):
    form = InferenceRuleForm()
    return render(request, 'index.html', {'form': form})