#!/bin/bash
source /home/dev/.bashrc
#apt-get install node npm
#npm run build
#/home/dev/.pyenv/versions/artconomy/bin/python -m pip install -r requirements.txt
if [[ ! -d node_modules ]]
   then
   cp -a /root/node_modules /app/
fi
./manage.py migrate
./manage.py initial_service_plans
./manage.py create_anonymous_user
#./manage.py stripe_webhooks --domain="$WEBHOOKS_DOMAIN"
npm run serve &
./manage.py collectstatic -v0 --noinput
#./manage.py tg_bot &
# Turning off ssl validation since our local dev cert is not valid.
NODE_TLS_REJECT_UNAUTHORIZED=0 npx companion &
exec "$@"
