.PHONY: all clean

IMAGE_NAME := serp_app
CONTAINER_NAME := serp_app_server
DOCKER_PORT := 8002
SERVICE_PORT := 8000
APP_DIR := /app
TEST_DIRS := tests/{api,jobs,models,services,utils}

all: run

clean: stop
	docker rmi --force $(IMAGE_NAME)

stop:
	if [ -z "$$(docker ps -a -q -f name=$(CONTAINER_NAME))" ]; then \
		echo "No container exists"; \
	else \
		docker stop $(CONTAINER_NAME); \
		docker rm --force $(CONTAINER_NAME); \
	fi

build:
	docker build -t $(IMAGE_NAME) .

run: stop build
	docker run -d --name $(CONTAINER_NAME) -p $(DOCKER_PORT):$(SERVICE_PORT) $(IMAGE_NAME)
	@echo "Type 'make open' to open websockets terminal"

test:
	docker exec -it $(CONTAINER_NAME) /bin/bash -c 'cd $(APP_DIR) && poetry run pytest ${TEST_DIRS} -v'

shell:
	docker exec -it $(CONTAINER_NAME) /bin/bash

console:
	docker exec -it $(CONTAINER_NAME) /bin/bash -c 'cd $(APP_DIR) && poetry run python app/console.py'

logs:
	docker logs -f $(CONTAINER_NAME)

ws_console:
	if ! command -v wscat &> /dev/null; then \
		npm install -g wscat; \
	fi
	wscat -c ws://localhost:$(DOCKER_PORT)/ws

health_check:
	@STATUS=$$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$(DOCKER_PORT)/health-check); \
	if [ "$$STATUS" -ne 200 ]; then \
		echo "Health check failed"; \
		exit 1; \
	fi

lines:
	wc -l $(APP_DIR)/{app,config,tests}/**/*.py ${APP_DIR}/bin/*

staging:
	git checkout main && \
	git pull origin main && \
	git checkout staging && \
	git pull origin staging && \
	git merge main && \
	git push origin staging && \
	git checkout main

production:
	git checkout main && \
	git pull origin main && \
	git checkout production && \
	git pull origin production && \
	git merge main && \
	git push origin production && \
	git checkout main

prod: production
