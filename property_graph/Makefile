

# 
.PHONY: help docker 

help:
	@echo "make help"
	@echo "      this message"
	@echo "==== Targets outside container ===="
	@echo "make up"
	@echo "      build and run docker"


up:
	docker-compose down
	docker-compose up --build --remove-orphans

down:
	docker-compose down
