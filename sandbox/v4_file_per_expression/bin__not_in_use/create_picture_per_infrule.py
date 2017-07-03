#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>

import sys
import os
lib_path = os.path.abspath('/Users/benpayne/version_controlled/proofofconcept/lib/')
sys.path.append(lib_path) # this has to proceed use of physgraph
import lib_physics_graph as physgraf

from os import listdir
from os.path import isfile, join

mypath='../inference_rules'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
# print onlyfiles
extension='png'

for this_filename in onlyfiles:
    split_filename=this_filename.split('.') 
    filename=split_filename[0]
    file_extension=split_filename[-1]
    split_filename=filename.split('_')
    infrule_name=split_filename[0]
#     print(filename+"  "+file_extension)
    if (file_extension=="tex"):
        latex_expression=infrule_name
        physgraf.make_picture_from_latex_expression(infrule_name,mypath,latex_expression,extension)

os.remove('tmp.aux')
os.remove('tmp.dvi')
os.remove('tmp.out')
os.remove('tmp.log')
os.remove('tmp.tex')