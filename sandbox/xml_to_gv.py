#!/usr/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>

import sys
import os
lib_path = os.path.abspath('lib')
sys.path.append(lib_path) # this has to proceed use of physgraph
db_path = os.path.abspath('databases')
sys.path.append(lib_path) # this has to proceed use of physgraph
import lib_physics_graph as physgraf
from xml.dom.minidom import parseString

#all these imports are standard on most modern python implementations

#open the xml file for reading:
file = open(db_path+'/statements_database.xml','r')
#convert to string:
data = file.read()
#close file because we dont need it anymore:
file.close()
#parse the xml you got from the file
dom = parseString(data)
#retrieve the first xml tag (<tag>data</tag>) that the parser finds with name tagName:
xmlTag = dom.getElementsByTagName('statement')[0].toxml()
#strip off the tag (<tag>data</tag>  --->   data):
xmlData=xmlTag.replace('<statement>','').replace('</statement>','')
print "\nprint out the xml tag and data in this format: <tag>data</tag>"
print xmlTag
print "\njust print the data"
print xmlData
