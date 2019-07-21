# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from main.forms import *


def add_inference_rule(request):
    inference_rule_form = InferenceRuleForm()
    return render(request, 'index.html', {'inference_rule_form': inference_rule_form})


def add_feed(request):
    feed_form = FeedForm()
    return render(request, 'index.html', {'feed_form': feed_form})


def add_expression(request):
    expression_form = ExpressionForm()
    return render(request, 'index.html', {'expression_form': expression_form})


def add_connection(request):
    connection_form = ConnectionForm()
    return render(request, 'index.html', {'connection_form': connection_form})


def add_symbol(request):
    symbol_form = SymbolForm()
    return render(request, 'index.html', {'symbol_form': symbol_form})
