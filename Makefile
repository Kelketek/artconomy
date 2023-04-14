default: install_prereqs build

APP_COMMAND=docker-compose exec -Tw /app web /bin/bash -lc
# Lower if you don't have a bunch of cores.
TEST_THREADS=10

install_prereqs:
	sudo apt install -y docker-compose docker-ce
	npm install

build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

shell:
	docker-compose exec web /bin/bash

test: test_frontend test_backend

test_frontend:
	${APP_COMMAND} "npm run test:unit"

test_backend:
	${APP_COMMAND} "./manage.py test --parallel=${TEST_THREADS}"

upgrade:
	rm -f requirements.txt && ${APP_COMMAND} "pip-compile --resolver=backtracking requirements.in constraints.in --output-file=requirements.txt"
	rm -f deploy_requirements.txt && ${APP_COMMAND} "pip-compile --resolver=backtracking deploy_requirements.in"
