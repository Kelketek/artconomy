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
	docker-compose up -d

logs:
	docker-compose logs -f --tail=1000

stop:
	docker-compose stop

restart: stop up

down:
	docker-compose down

shell:
	docker-compose exec web /bin/bash

test: test_frontend test_backend

test_frontend:
	${APP_COMMAND} "npm run test"

test_backend:
	${APP_COMMAND} "./manage.py test --keepdb --parallel=${TEST_THREADS}"

format:
	${APP_COMMAND} "npm run lint:fix"
	${APP_COMMAND} "black backend"
	${APP_COMMAND} "ruff --fix backend"

upgrade:
	rm -f requirements.txt && ${APP_COMMAND} "pip-compile --resolver=backtracking requirements.in constraints.in --output-file=requirements.txt"
	rm -f deploy_requirements.txt && ${APP_COMMAND} "pip-compile --resolver=backtracking deploy_requirements.in"
