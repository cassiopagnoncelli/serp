.PHONY: all clean

IMAGE_NAME := serp_app
CONTAINER_NAME := serp_app_server
DOCKER_PORT := 8002
SERVICE_PORT := 8000
APP_DIR := /app

all: run

clean: stop
	docker rmi --force $(IMAGE_NAME)

stop:
	if [ -z "$$(docker ps -a -q -f name=$(CONTAINER_NAME))" ]; then \
		echo "No container exists"; \
	else \
		docker rm --force $(CONTAINER_NAME); \
	fi

build:
	docker build -t $(IMAGE_NAME) .

run: stop build
	docker run -d --name $(CONTAINER_NAME) -p $(DOCKER_PORT):$(SERVICE_PORT) $(IMAGE_NAME)
	@echo "Type 'make open' to open websockets terminal"

shell:
	docker exec -it $(CONTAINER_NAME) /bin/bash

console:
	docker exec -it $(CONTAINER_NAME) bash -c 'cd $(APP_DIR) && poetry run python app/console.py'

logs:
	docker logs -f $(CONTAINER_NAME)

websocket:
	wscat -c ws://localhost:$(DOCKER_PORT)/ws

prod:
	git checkout main && \
	git pull origin main && \
	git checkout staging && \
	git pull origin staging && \
	git merge main && \
	git push origin staging && \
	git checkout main

prod:
	git checkout main && \
	git pull origin main && \
	git checkout production && \
	git pull origin production && \
	git merge main && \
	git push origin production && \
	git checkout main
