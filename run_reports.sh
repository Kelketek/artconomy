#! /bin/bash
# This script is used on dev machines to process card reports from EVO. You must first download all transactions/settlements before
# running it. That is, go to https://www.mymerchant.info/ and log in, then choose:
# Transactions -> Settlements
# ...and select a date range much wider than you need into the past up until today. Then hit Submit, then hit the dropdown triangle
# on the Export button to select the export template 'source_transactions_csv'. Save the file right into this directory.
# Now, repeat the above process, but instead of going to Transactions -> Settlements, go to:
# Billing and Deposits -> Funds Settled
# ...and then the export dropdown should read: settled_csv
# Download the file right into this directory.
# DON'T CHANGE THE FILE NAMES!

# Fast fail. If anything doesn't work, just die and don't continue.
set -e
TRANSACTIONS_FILE=transactions.csv
SETTLEMENTS_FILE=settlements.csv
PROCESSED_FILE=processed.csv
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ACTIVATION_SCRIPT="${SCRIPT_DIR}/../env/bin/activate"
REPORTS_DIR="reports/financial/$(date +'%B-%d-%Y')"
# This is only to be run within docker for now, so we need the path for docker.
DUMP_FILE="/app/ansible/production.sql"
CARD_TRANSACTIONS_FILE="${REPORTS_DIR}/card_transactions.csv"

cd "${SCRIPT_DIR}"
source "${ACTIVATION_SCRIPT}"
cd "${SCRIPT_DIR}/ansible"
ansible-playbook -i inventory dump.yml
cd "${SCRIPT_DIR}"
docker exec -i artconomy_web_1 /bin/bash <<EOF
set -e
./manage.py replace_db < "${DUMP_FILE}"
./manage.py settlement --transactions="${TRANSACTIONS_FILE}" --settlements="${SETTLEMENTS_FILE}" > "${PROCESSED_FILE}"
mkdir -p "${REPORTS_DIR}"
./manage.py fees --processed "${PROCESSED_FILE}" > "${CARD_TRANSACTIONS_FILE}"
EOF
cp -a "${REPORTS_DIR}" ~/Nextcloud/work/Books/
