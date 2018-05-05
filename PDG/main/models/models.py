# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models


class InferenceRules(models.Model):
    inference_rule_name = models.CharField(max_length=128, null=True)
    number_of_arguments = models.IntegerField(max_length=128, null=True)
    number_of_feeds = models.IntegerField(null=True)
    number_of_input_expressions = models.IntegerField(null=True)
    number_of_output_expressions = models.IntegerField(null=True)
    comments = models.CharField(max_length=128, null=True)
    latex_expression = models.CharField(max_length=128, null=True)
