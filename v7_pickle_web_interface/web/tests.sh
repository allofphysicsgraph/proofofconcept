#!/bin/bash

# https://sipb.mit.edu/doc/safe-shell/
set -euf -o pipefail
set -o

# type hinting verification
mypy --check-untyped-defs compute.py
read -rsp $'Press any key to continue...\n' -n1 key
mypy --check-untyped-defs controller.py 
read -rsp $'Press any key to continue...\n' -n1 key

flake8 --ignore E701,E501,W291,E302 compute.py
read -rsp $'Press any key to continue...\n' -n1 key
flake8 controller.py
read -rsp $'Press any key to continue...\n' -n1 key

pylint compute.py
read -rsp $'Press any key to continue...\n' -n1 key
pylint controller.py
read -rsp $'Press any key to continue...\n' -n1 key

python3 -m doctest -v compute.py
read -rsp $'Press any key to continue...\n' -n1 key
python3 -m doctest -v controller.py
read -rsp $'Press any key to continue...\n' -n1 key

read -rsp $'Press any key to continue...\n' -n1 key
python3 -m mccabe compute.py
read -rsp $'Press any key to continue...\n' -n1 key
python3 -m mccabe controller.py

