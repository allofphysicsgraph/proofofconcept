# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.apps import apps

# https://stackoverflow.com/questions/9443863/register-every-table-class-from-an-app-in-the-django-admin-page
app = apps.get_app_config('main')
for model_name, model in app.models.items():
    admin.site.register(model)