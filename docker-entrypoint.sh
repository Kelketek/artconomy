#!/bin/bash
#apt-get install node npm
#npm run build
/usr/bin/python3.8 -m pip install -r requirements.txt
ln -s /app/dev_settings.json /settings.json
if [[ ! -d node_modules ]]
   then
   cp -a /root/node_modules /app/
   ./manage.py collectstatic -v0 --noinput
fi
./manage.py migrate
npm run serve &
./manage.py tg_bot &
exec "$@"
