# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class URLS(models.Model):
    url=models.CharField(max_length=800)

class FIELDS_PHYSICS(models.Model):
    field = models.CharField(max_length=100)


class OPERATORS(models.Model):
    operator = models.IntegerField()
    number_of_args=models.IntegerField()
    input_line_count=models.IntegerField()
    output_line_count=models.IntegerField()
    latex_function_desc=models.CharField(max_length=250)


#<unique id>,<symbol>,<type>,<value>,<units>,<description>,<cas_sympy>
class SYMBOLS(models.Model):
    id=models.IntegerField(primary_key=True)
    symbol = models.IntegerField()
    type=models.IntegerField()
    value=models.IntegerField()
    units=models.IntegerField()
    description=models.CharField(max_length=250)
    cas_sympy = models.CharField(max_length=250)

class Derivation(models.Model):
        expression = models.CharField(max_length=250, blank=False, null=True)
        goal = models.CharField(max_length=250, blank=False, null=True)
