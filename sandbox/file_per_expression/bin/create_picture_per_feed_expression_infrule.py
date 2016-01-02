#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>

import sys.path
import os.path
lib_path = os.path.abspath('/Users/benpayne/version_controlled/proofofconcept/lib/')
sys.path.append(lib_path) # this has to proceed use of physgraph
import lib_physics_graph as physgraf

from os import listdir
from os.path import isfile, join

mypath='../feeds'
# mypath='../expressions'
# mypath='../inference_rules'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
# print onlyfiles
extension='png'

for this_filename in onlyfiles:
    split_filename=this_filename.split('.') 
    filename=split_filename[0]
    file_extension=split_filename[-1]
#     print(filename+"  "+file_extension)
    if (file_extension=="tex"):
        with open(mypath+"/"+this_filename, 'r') as f:
            read_data = f.read()
#         print(read_data.rstrip())
        latex_expression="$"+read_data.rstrip()+"$"
        physgraf.make_picture_from_latex_expression(filename,mypath,latex_expression,extension)

