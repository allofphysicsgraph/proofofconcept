import time 
import random
import re
import os
import sys
import yaml
import os.path
import subprocess


lib_path = os.path.abspath('../lib')
sys.path.append(lib_path)  # this has to proceed use of physgraph
import lib_physics_graph as physgraf

# https://yaml-online-parser.appspot.com/
input_stream = file('config.input', 'r')
input_data = yaml.load(input_stream)

