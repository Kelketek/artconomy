#! /bin/bash
# This script copies the live DB down and runs migrations to verify that any local changes don't break things.

# Fast fail. If anything doesn't work, just die and don't continue.
set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
# User ID to chown report file to. Should match the UID of host user so that it can be worked with.
TARGET_UID=1000
# This is only to be run within docker for now, so we need the path for docker.
DUMP_FILE="/home/app/artconomy/ansible/production.sql"

cd "${SCRIPT_DIR}/ansible"
#ansible-playbook -i keys/inventory dump.yml
cd "${SCRIPT_DIR}"
docker exec -i artconomy-web-1 /bin/bash <<EOF
set -e
./manage.py replace_db < "${DUMP_FILE}"
./manage.py migrate
EOF
