

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
