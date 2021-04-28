# specify the node base image with your desired version node:<version>
FROM ubuntu
# replace this with your application's default port
EXPOSE 8001
EXPOSE 8002
ENV PYTHONUNBUFFERED 1
WORKDIR /root
RUN apt-get update
RUN apt-get update --fix-missing
RUN apt-get install software-properties-common apt-utils -y
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt-get update
RUN apt-get install python3-pip python3.8 python3.8-dev build-essential npm curl git wget postgresql-client psmisc libpq-dev -y
RUN apt-get upgrade -y
RUN apt-get autoremove -y
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get install -y nodejs
RUN mkdir /app
RUN groupadd -g 1000 dev
RUN useradd -u 1000 -d /app -g dev dev
RUN chown 1000:1000 /app
WORKDIR /app
USER 1000
ADD . .
ENV LANG=C.UTF-8
#RUN /usr/bin/python3.8 -m pip install --upgrade pip
#RUN /usr/bin/python3.8 -m pip install -r requirements.txt
# RUN npm install
# RUN npm run build
#RUN npm run build
#RUN ./manage.py collectstatic -v0 --noinput
# RUN mv node_modules /root
