# Creative Commons Attribution 4.0 International License
# https://creativecommons.org/licenses/by/4.0/

# this Makefile contains targets for use inside the Docker container and on the baremetal host

# 
.PHONY: help clean webserver typehints flake8 pylint doctest mccabe

help:
	@echo "make help"
	@echo "      this message"
	@echo "==== Targets outside container ===="
	@echo "make docker"
	@echo "      build and run docker"
	@echo "make dockerlive"
	@echo "      build and run docker /bin/bash"
	@echo "==== Targets inside container ===="
	@echo "make flask"
	@echo "      start webserver"
	@echo "make gunicorn"
	@echo "      start webserver"
	@echo "make black"
	@echo "      format py files"
	@echo "make clean"
	@echo "      remove extra files"
	@echo "make typehints FILE_NAME=controller.py"
	@echo "      typehints for all dependent .py files"
	@echo "make flake8"
	@echo "      for all .py files; make flake8"
	@echo "make pycallgraph"
	@echo "make prospector"
	@echo "make pylint  FILE_NAME=controller.py"
	@echo "make pylint  FILE_NAME=compute.py"
	@echo "make doctest FILE_NAME=controller.py"
	@echo "make doctest FILE_NAME=compute.py"
	@echo "make mccabe  FILE_NAME=controller.py"
	@echo "make mccabe  FILE_NAME=compute.py"

ifdef FILE_NAME
	@echo 'FILE_NAME is defined' $(FILE_NAME)
else
	@echo 'FILE_NAME is undefined'
endif

docker:
	docker build -t flask_ub .
	docker run -it --rm -v`pwd`/data.json:/home/appuser/app/data.json \
           -v`pwd`/logs/:/home/appuser/app/logs/ \
           -v`pwd`/users_sqlite.db:/home/appuser/app/users_sqlite.db \
           --env-file .env --publish 5000:5000 flask_ub

dockerlive:
	docker build -t flask_ub .
	docker run -it --rm -v`pwd`:/scratch \
           -v`pwd`/data.json:/home/appuser/app/data.json \
           -v`pwd`/logs/:/home/appuser/app/logs/ \
           -v`pwd`/users_sqlite.db:/home/appuser/app/users_sqlite.db \
           --env-file .env --entrypoint='' \
           --publish 5000:5000 flask_ub /bin/bash

neo4j:
	docker run --publish=7474:7474 --publish=7687:7687 --publish=7473:7473 \
           --volume=$$HOME/neo4j/data:/data \
           --volume=$$HOME/neo4j/logs:/logs \
           --volume=$$HOME/neo4j/conf:/conf \
           --volume=$$HOME/neo4j/tmp:/tmp \
           --env NEO4J_AUTH=none neo4j:4.0

flask:
	python3 controller.py

# https://docs.gunicorn.org/en/stable/
# Gunicorn ‘Green Unicorn’ is a Python WSGI HTTP Server for UNIX.
gunicorn:
	gunicorn --bind 0.0.0.0:5000 wsgi:app

# https://mypy.readthedocs.io/en/stable/
# Mypy is a static type checker
typehints:
	mypy --check-untyped-defs $(FILE_NAME)

# https://pycallgraph.readthedocs.io/en/master/
# creates call graph visualizations
pycallgraph:
	pycallgraph graphviz -- ./controller.py

# http://prospector.landscape.io/en/master/
# analyze Python code and output information about errors, 
# potential problems, convention violations and complexity.
prospector:
	prospector

# https://flake8.pycqa.org/en/latest/
# enforce style consistency across Python projects.
flake8:
	flake8 --ignore W291,E115,E121,E122,E124,E126,E127,E128,E203,E221,E225,E231,E241,E251,E261,E265,E302,E303,E501,E701
# E115 expected an indented block
# E121 continuation line under-indented for hanging indent
# E122 continuation line missing indentation or outdented
# E124 closing bracket does not match visual indentation
# E126 continuation line over-indented for hanging indent
# E127 Continuation line over-indented for visual indent; https://www.flake8rules.com/rules/E127.html
# E128 continuation line under-indented for visual indent
# E203 whitespace before
# E221 multiple spaces before operator
# E225 missing whitespace around operator
# E231 missing whitespace after ','
# E241 multiple spaces after ','
# E251 unexpected spaces around keyword / parameter equals
# E261 at least two spaces before inline comment
# E265 block comment should start with '# '
# E302 Expected 2 blank lines, found 0; https://www.flake8rules.com/rules/E302.html
# E303 too many blank lines
# E501 Line too long; https://www.flake8rules.com/rules/E501.html
# E701 Multiple statements on one line; https://www.flake8rules.com/rules/E701.html

# https://black.readthedocs.io/en/stable/
# By using Black, you agree to cede control over minutiae of hand-formatting.
black:
	black common_lib.py
	black compute.py
	#black config.py
	black controller.py
	#black convert_v3_csv_infrules_to_dict.py
	black validate_steps_sympy.py
	black validate_dimensions_sympy.py
	black latex_to_sympy.py
	#black wsgi.py
	black inference_rules.py

# https://www.pylint.org/
# http://pylint.pycqa.org/en/latest/
# checks for errors in Python code, tries to enforce a coding standard and looks for code smells.
pylint:
	pylint $(FILE_NAME)

# https://docs.python.org/3/library/doctest.html
# searches for pieces of text that look like interactive Python sessions, and 
# then executes those sessions to verify that they work exactly as shown.
doctest:
	python3 -m doctest -v $(FILE_NAME)

# https://pypi.org/project/mccabe/
# check McCabe complexity; see
# https://en.wikipedia.org/wiki/Cyclomatic_complexity
mccabe:
	python3 -m mccabe $(FILE_NAME)

clean:
	rm *.log *.tex *.pdf *.txt

# EOF
