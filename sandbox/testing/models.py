# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#from django.db import models


class InferenceRule(models.Model):
    inference_rule_name = models.CharField(max_length=128,null=True)
    number_of_arguments = models.IntegerField(null=True)
    number_of_feeds = models.IntegerField(null=True)
    number_of_input_expressions = models.IntegerField(null=True)
    number_of_output_expressions = models.IntegerField(null=True)
    comments = models.CharField(max_length=128, null=True)
    latex_expression = models.CharField(max_length=128, null=True)


class Feed(models.Model):
    index = models.IntegerField(null=True)
    latex = models.CharField(max_length=128, null=True)


class Expression(models.Model):
    index = models.IntegerField(null=True)
    latex = models.CharField(max_length=128, null=True)


class Connection(models.Model):
    derivation_name = models.IntegerField(null=True)
    step_index = models.CharField(max_length=128, null=True)
    input_type = models.IntegerField(null=True)
    input_temporary_index = models.CharField(max_length=128, null=True)
    input_permanent_index = models.IntegerField(null=True)
    output_type = models.CharField(max_length=128, null=True)
    output_temporary_index = models.IntegerField(null=True)
    output_permanent_index = models.CharField(max_length=128, null=True)


class Symbol(models.Model):
    unique_id = models.IntegerField(null=True)
    symbol = models.CharField(max_length=128,null=True)
    type = models.CharField(max_length=128,null=True)
    value = models.FloatField(null=True)
    units = models.CharField(max_length=128,null=True)
    description = models.CharField(max_length=128,null=True)
    cas_sympy = models.CharField(max_length=128,null=True)
