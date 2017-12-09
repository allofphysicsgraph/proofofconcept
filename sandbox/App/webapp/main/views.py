# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from models import *
import requests
import re
from os import listdir
import re, os
import os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from os import system
from time import sleep
import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('postgres://pdg_user:password@localhost/pdg')



path='/home/user/PycharmProjects/proofofconcept/sandbox/App/webapp/main/static/pdfs'


def wiki_index(request):
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

    return render(request,'b_index.html',context)



def create_symbols_table():
    import pandas as pd
    from string import printable
    printable_strings = set(printable)

    def remove_unicode_chars(strng):
        return ''.join([x for x in strng if x in printable_strings])

    f = open('/home/user/PycharmProjects/proofofconcept/sandbox/App/webapp/main/databases/symbols_database.csv')
    df = pd.read_csv(f, names=['id', 'symbol', 'type', 'value', 'units', 'description', 'cas_sympy'])
    df = df.applymap(lambda x: remove_unicode_chars(str(x)))
    df.dropna(inplace=True)
    df.to_sql('symbols', engine, if_exists='replace')






def index_pdfs(request):
    testing = system('find {} -name "*.pdf" > /tmp/pdfs'.format(path))
    system('cat /tmp/pdfs |rev|cut -d "/" -f1 |rev >/tmp/pdf_files')
    return render(request,'index.html')

def pdfs(request):
    #f=open('/tmp/pdf_files')
    #files = f.readlines()
    #f.close()
    files=''
    try:
        df = pd.read_sql('symbols', engine).fillna(' ')
    except:
        create_symbols_table()
        df = pd.read_sql('symbols', engine).fillna(' ')
    columns = [x for x in df.columns.tolist() if x != 'id']
    symbols_rows = df.iterrows()
    context = {

        'files': files,
        'columns': columns,
        'rows': symbols_rows,

    }

    return render(request,'data_table.html',context)


def pdf_list(request):
    testing = system('find {} -name "*.pdf"'.format(path))



#https://stackoverflow.com/questions/11779246/how-to-show-a-pdf-file-in-a-django-view
@csrf_exempt
def render_pdf(request):

    file_name=request.get_full_path()
    f=open('/tmp/pdfs')
    data=f.readlines()
    fname=[x.replace('\n','') for x in data if file_name in str(x)][0]
    name = fname

    with open(name, 'r') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline;filename='+name+'.pdf'
            return response
            pdf.closed




def wolfram_query(request):
    #https: // pypi.python.org / pypi / wolframalpha

    #https: // developer.wolframalpha.com / portal / myapps /

    import wolframalpha  # https://pypi.python.org/pypi/wolframalpha

    f = open('wolfram_app_id', 'r')
    appid = f.read()
    f.close()
    appid = appid.rstrip()  # http://effbot.org/pyfaq/is-there-an-equivalent-to-perl-s-chomp-for-removing-trailing-newlines-from-strings.htm

    client = wolframalpha.Client(appid)  # http://products.wolframalpha.com/api/documentation.html



def ntwrkx_dir_grph():
    import networkx as nx
    # https://trac.macports.org/ticket/31891
    import sys
    sys.path.reverse()
    import matplotlib.pyplot as plt

    # http://networkx.lanl.gov/tutorial/tutorial.html
    # http://networkx.lanl.gov/reference/classes.digraph.html
    G = nx.DiGraph()
    G.add_node(1)
    G.add_node(2)
    G.add_node(3)
    G.add_node(4)
    G.add_edge(1, 2)
    G.add_edge(3, 4)
    G.add_edge(1, 4)
    nx.draw(G)
    plt.show()

def wolfram_response():
    import urllib
    import urllib.request
    import xml.etree.ElementTree as ET  # http://stackoverflow.com/questions/15442130/python-xml-parsing-for-wolfram-api

    f = open('wolfram_app_id', 'r')
    appid = f.read()
    f.close()
    appid = appid.rstrip()  # http://effbot.org/pyfaq/is-there-an-equivalent-to-perl-s-chomp-for-removing-trailing-newlines-from-strings.htm

    xml_data = urllib.request.urlopen(
        "http://api.wolframalpha.com/v2/query?input=sqrt+2&appid=APLTT9-9WG78GYE65").read()
    root = ET.fromstring(xml_data)

    for pod in root.findall('.//pod'):
        print(pod.attrib['title'])
        for pt in pod.findall('.//plaintext'):
            if pt.text:
                print('-', pt.text)

def create_ast():
    from sys import argv
    import ast
    from astmonkey import visitors, transformers
    f = open(argv[1])
    node = ast.parse(f.read())
    node = transformers.ParentNodeTransformer().visit(node)
    visitor = visitors.GraphNodeVisitor()
    visitor.visit(node)
    visitor.graph.write_dot('test')


def clean_ast():
    import re
    f = open('test')
    g = open('ast_output', 'w')
    data = f.read()
    for item in re.split('\s{2,}', data):
        match = re.findall('^<.*|label.*', item)
        if len(match) > 0:
            g.write(match[0])

    g.close()

    h = open('ast_output')
    data_2 = h.read()

    data_3 = re.sub('_ast.|object at', '', data_2)

    data_4 = re.sub(',<', '\n<', data_3)

    print(data_4)

    i = open('parsed_ast_output', 'w')
    i.write(data_4)
    i.write('\n')
    for label in re.findall('label.*', data_4):
        print(label)
        i.write(label)
        i.write('\n')

    i.close()



def xml_to_gv():
    # !/usr/local/bin/python
    # Physics Equation Graph
    # Ben Payne <ben.is.located@gmail.com>

    import sys
    import os
    lib_path = os.path.abspath('lib')
    sys.path.append(lib_path)  # this has to proceed use of physgraph
    db_path = os.path.abspath('databases')
    sys.path.append(lib_path)  # this has to proceed use of physgraph
    import lib_physics_graph as physgraf
    from xml.dom.minidom import parseString

    # all these imports are standard on most modern python implementations

    # open the xml file for reading:
    file = open(db_path + '/statements_database.xml', 'r')
    # convert to string:
    data = file.read()
    # close file because we dont need it anymore:
    file.close()
    # parse the xml you got from the file
    dom = parseString(data)
    # retrieve the first xml tag (<tag>data</tag>) that the parser finds with name tagName:
    xmlTag = dom.getElementsByTagName('statement')[0].toxml()
    # strip off the tag (<tag>data</tag>  --->   data):
    xmlData = xmlTag.replace('<statement>', '').replace('</statement>', '')
    print "\nprint out the xml tag and data in this format: <tag>data</tag>"
    print xmlTag
    print "\njust print the data"
    print xmlData


def derivation(request):
    from models import Derivation
    from forms import MyModelForm
    context_data = {}
    if request.method == 'POST':
            form = MyModelForm(request.POST)

            if form.is_valid():
                # save the model to database, directly from the form:
                form.save()  # reference to my_model is often not needed at all, a simple form.save() is ok
                # alternatively:
                # my_model = form.save(commit=False)  # create model, but don't save to database
                # my.model.something = whatever  # if I need to do something before saving it
                # my.model.save()
    else:
        form = MyModelForm()
        context_data = {'form': form}


    print context_data
    return render(request,'derivation.html', context_data)
