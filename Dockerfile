# specify the node base image with your desired version node:<version>
FROM node:8
# replace this with your application's default port
EXPOSE 8888
ENV PYTHONUNBUFFERED 1
WORKDIR /app
RUN apt-get update
RUN apt-get install python3-pip python3-dev build-essential npm -y
#RUN apt-get install python-pip -y
RUN pip3 install --upgrade pip
RUN pwd
RUN ls -la
RUN pip3 install -r requirements.txt
RUN npm install
RUN npm rebuild node-sass --force
RUN npm run build
RUN ls -la
RUN ./manage.py collectstatic -v0 --noinput
