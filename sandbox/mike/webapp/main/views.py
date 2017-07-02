# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from models import *
# Create your views here.


def index(request):
    import requests
    import re

    data = requests.get('https://en.wikipedia.org/wiki/Physics').content
    for url in re.findall('href="(.*?/wiki/.*?title.*?)(?:>|</a)', data):
        instance = URLS()
        instance.url = url
        try:
            instance.save()
        except:
            pass
    urls=[x for x in URLS.objects.all().values()]

    context={
        'urls':urls,
    }

    return render(request,'index.html',context)











