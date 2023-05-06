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


up:
	# https://docs.docker.com/compose/reference/down/
	docker-compose down --volumes --remove-orphans
	# https://docs.docker.com/compose/reference/up/
	docker-compose up --build --remove-orphans

down:
	docker-compose down

black_out:
	docker run --rm -v`pwd`:/scratch --entrypoint='' -w /scratch/ property_graph_webserver make black_in

black_in:
	black webserver/app.py webserver/neo4j_query.py
