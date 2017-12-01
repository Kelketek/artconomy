# specify the node base image with your desired version node:<version>
FROM node:8
# replace this with your application's default port
EXPOSE 8888
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
RUN apt-get update
RUN apt-get install python3-pip python3-dev build-essential npm -y
RUN pip3 install --upgrade pip
RUN ls -la
