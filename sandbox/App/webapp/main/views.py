# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from models import *
# Create your views here.


def inde(request):
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


import re, os
import os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

#https://stackoverflow.com/questions/11779246/how-to-show-a-pdf-file-in-a-django-view
@csrf_exempt
def index(request):
    #name = request.GET.get('name', "")

    #filename = "path/to/file"+name+".pdf"
    filename='/home/user/Desktop/pelicanhpc.pdf'
    try:
        if not re.search("^[a-zA-Z0-9]+$",name):
            raise ValueError("Filename wrong format")
        elif not os.path.isfile(filename):
            raise ValueError("Filename doesn't exist")
        else:
            with open(filename, 'r') as pdf:
                response = HttpResponse(pdf.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'inline;filename='+name+'.pdf'
                return response
            pdf.closed
    except ValueError as e:
        HttpResponse(e.message)








