from django.views.generic import TemplateView
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from django.core.management import call_command
import pickle
import json
from time import time
import re

client = settings.REDIS_CLIENT


class HomeView(TemplateView):
    template_name = 'index.html'
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['port_list'] = {'a':1}
        return context
