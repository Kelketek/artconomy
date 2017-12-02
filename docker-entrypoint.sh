#!/bin/bash
#apt-get install node npm
#npm run build
pip3 install -r requirements.txt
if [[ ! -d node_modules ]]
   then
   npm install
   npm rebuild node-sass --force
   ./manage.py collectstatic -v0 --noinput
fi
./manage.py migrate
npm run dev &
exec "$@"
