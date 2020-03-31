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
RUN apt-get install python3-pip python3.8 python3.8-dev build-essential npm firefox curl git xvfb wget postgresql-client psmisc libpq-dev -y
RUN apt-get upgrade -y
RUN apt-get autoremove -y
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get install -y nodejs
RUN wget "https://github.com/mozilla/geckodriver/releases/download/v0.21.0/geckodriver-v0.21.0-linux64.tar.gz"
RUN tar -xvzf geckodriver-v0.21.0-linux64.tar.gz
RUN rm geckodriver-v0.21.0-linux64.tar.gz
RUN chmod +x geckodriver
RUN cp geckodriver /usr/local/bin/
RUN mkdir /app
WORKDIR /app
ADD . .
ENV LANG=C.UTF-8
RUN /usr/bin/python3.8 -m pip install --upgrade pip
RUN /usr/bin/python3.8 -m pip install -r requirements.txt
# RUN npm install
# RUN npm run build
#RUN npm run build
#RUN ./manage.py collectstatic -v0 --noinput
# RUN mv node_modules /root
