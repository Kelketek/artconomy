default: install_prereqs up collectstatic migrate initial_service_plans create_anonymous_user install_frontend_prereqs rust build_frontend

APP_COMMAND=docker compose exec web
FRONTEND_COMMAND=docker compose exec frontend
# Lower if you don't have a bunch of cores.
TEST_THREADS=10

.PHONY: rust

install_prereqs:
	sudo apt install -y docker docker-ce

install_frontend_prereqs:
	${FRONTEND_COMMAND} npm install

build:
	docker compose build

build_frontend:
	${FRONTEND_COMMAND} npm run build

migrate: ## run migration
	${APP_COMMAND} ./manage.py migrate

collectstatic: ## run collectstatic
	${APP_COMMAND} ./manage.py collectstatic -v0 --noinput

initial_service_plans:
	${APP_COMMAND} ./manage.py initial_service_plans

create_anonymous_user:
	${APP_COMMAND} ./manage.py create_anonymous_user

up:
	docker compose up -d

logs:
	docker compose logs -f --tail=1000

stop:
	docker compose stop

restart: stop up

down:
	docker compose down

shell:
	docker compose exec web /bin/bash

test: test_frontend test_backend

rust:
	wasm-pack build --dev --target=bundler --out-dir=../../frontend/lib/lines rust/line_items --features=wasm
	${APP_COMMAND} bash -lc "cd rust/line_items && maturin sdist && pip install --force-reinstall target/wheels/line_items-0.1.0.tar.gz"

test_frontend:
	${APP_COMMAND} npm run test

test_backend:
	${APP_COMMAND} ./manage.py test --keepdb --parallel=${TEST_THREADS}

format:
	${FRONTEND_COMMAND} npm run lint:fix
	${APP_COMMAND} black backend
	${APP_COMMAND} ruff --fix backend

upgrade:
	rm -f requirements.txt && ${APP_COMMAND} pip-compile --resolver=backtracking requirements.in constraints.in --output-file=requirements.txt
	rm -f deploy_requirements.txt && ${APP_COMMAND} pip-compile --resolver=backtracking deploy_requirements.in
	@# Must do this because absolute paths aren't the same between stage, production, and docker.
	@# There's a caveat, though. You MUST run pip install from the same directory as the requirements.txt.
	sed -i 's#.*file:///home/app/artconomy/#./#g' requirements.txt
