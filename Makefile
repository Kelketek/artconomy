default: install_prereqs build

APP_COMMAND=docker compose exec -Tw /app web /bin/bash -lc
# Lower if you don't have a bunch of cores.
TEST_THREADS=10

.PHONY: rust

install_prereqs:
	sudo apt install -y docker docker-ce
	# Need to replace this with a frontend container.
	#npm install

build:
	docker compose build

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
	@# This filename might change periodically, but probably not until we upgrade the OS, or increment the rust package's
	@# version.
	${APP_COMMAND} "cd rust/line_items && maturin build --features python && pip install --force-reinstall target/wheels/line_items-0.1.0-cp311-cp311-manylinux_2_34_x86_64.whl"

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
	@# Must do this because absolute paths aren't the same between stage, production, and docker.
	@# There's a caveat, though. You MUST run pip install from the same directory as the requirements.txt.
	sed -i 's#.*file:///app/#./#g' requirements.txt
