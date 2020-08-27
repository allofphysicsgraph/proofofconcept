# Creative Commons Attribution 4.0 International License
# https://creativecommons.org/licenses/by/4.0/

# 
.PHONY: help clean webserver typehints flake8 pylint doctest mccabe

help:
	@echo "make help"
	@echo "      this message"
	@echo "make docker"
	@echo "      build and run docker"
	@echo "make dockerlive"
	@echo "      build and run docker /bin/bash"

docker:
	docker build -t flask_ub .
	docker run -it --rm \
            --publish 5000:5000 flask_ub

dockerlive:
	docker build -t flask_ub .
	docker run -it --rm -v`pwd`:/scratch \
           --publish 5000:5000 flask_ub /bin/bash

