# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class URLS(models.Model):
    url=models.CharField(max_length=800)

class FIELDS_PHYSICS(models.Model):
    field = models.CharField(max_length=100)
