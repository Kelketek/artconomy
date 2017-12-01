#!/bin/bash
#apt-get install node npm
#npm run build
./manage.py migrate
npm run build &
exec "$@"
