#!/opt/local/bin/python
# Ben Payne <ben.is.located@gmail.com>
# Physics Derivation Graph
# 20160129

from os.path import isfile, join
from os import listdir
import lib_physics_graph as physgraf
import sys
import os
lib_path = os.path.abspath(
    '/Users/benpayne/version_controlled/proofofconcept/lib/')
sys.path.append(lib_path)  # this has to proceed use of physgraph

if (len(sys.argv) > 1):
    input_list = sys.argv
    print 'Number of arguments:', len(input_list), 'arguments.'
    print 'Argument List:', input_list
    filename = input_list[1]
    print("input name: " + filename)
else:
    print("example: \n")
    print("   no trailing slash\n")
    print("   python bin/create_png_for_nodes__input_filename_for_latex.py \"expressions/9999999989_latex_20151229.tex\"\n")
    exit()


picture_extension = 'png'

split_on_slash_filename = filename.split('/')
folder_name = '/'.join(
    split_on_slash_filename[0:len(split_on_slash_filename) - 1])
filename_with_extension = split_on_slash_filename[-1]
split_on_dot_filename = filename_with_extension.split('.')
file_extension = split_on_dot_filename[-1]
filename_without_extension = split_on_dot_filename[0]
split_on_underscore_filename = filename_without_extension.split('_')
output_filename_no_extension = split_on_underscore_filename[0]

print(
    "foldername: " +
    folder_name +
    "; file name with extension: " +
    filename_with_extension +
    "; file extension:  " +
    file_extension +
    "; filename without extension: " +
    filename_without_extension)
if (file_extension != 'tex'):
    print("filename extension should be .tex")
    exit()

with open(folder_name + "/" + filename_with_extension, 'r') as f:
    read_data = f.read()
    print(read_data.rstrip())
    latex_expression = "$" + read_data.rstrip() + "$"
    physgraf.make_picture_from_latex_expression(
        output_filename_no_extension,
        folder_name,
        latex_expression,
        picture_extension)

os.remove('tmp.aux')
os.remove('tmp.dvi')
os.remove('tmp.out')
os.remove('tmp.log')
os.remove('tmp.tex')
