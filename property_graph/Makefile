# Ben Payne
# Physics Derivation Graph
# https://allofphysics.com

#
.PHONY: help docker

help:
	@echo "make help"
	@echo "      this message"
	@echo "==== Targets outside container ===="
	@echo "make up"
	@echo "      build and run docker"

# create and start the webserver. This will build the Docker image if that's needed
up:
	if (! docker stats --no-stream ); then  open /Applications/Docker.app; while (! docker stats --no-stream ); do    echo "Waiting for Docker to launch...";  sleep 1; done; fi; docker-compose down --volumes --remove-orphans; docker-compose up --build --remove-orphans

# possibly to add as new target:
# make black_out; docker ps | grep property | cut -d' ' -f1 | xargs docker kill; date; make up

up_DEPRECATED:
	# https://docs.docker.com/compose/reference/down/
	docker-compose down --volumes --remove-orphans
	# https://docs.docker.com/compose/reference/up/
	docker-compose up --build --remove-orphans

down:
	docker-compose down

black_out:
	docker run --rm -v`pwd`:/scratch --entrypoint='' -w /scratch/ property_graph_webserver make black_in

black_in:
	black webserver/app.py webserver/neo4j_query.py webserver/compute.py

mypy_out:
	docker run --rm -v`pwd`:/scratch --entrypoint='' -w /scratch/ property_graph_webserver mypy --check-untyped-defs webserver/app.py


