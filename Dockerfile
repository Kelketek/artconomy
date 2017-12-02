# specify the node base image with your desired version node:<version>
FROM node:8
# replace this with your application's default port
EXPOSE 8001
EXPOSE 8002
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
ADD . .
RUN apt-get update
RUN apt-get install python3-pip python3-dev build-essential npm -y
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN npm install
RUN ./manage.py migrate
RUN ./manage.py collectstatic -v0 --noinput