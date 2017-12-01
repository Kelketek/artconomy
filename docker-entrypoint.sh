#!/bin/bash
#apt-get install node npm
#npm run build
pip3 install -r requirements.txt
npm install
npm rebuild node-sass --force
npm run build
./manage.py collectstatic
./manage.py migrate
npm run build &
exec "$@"
