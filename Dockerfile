# specify the node base image with your desired version node:<version>
FROM ubuntu
# replace this with your application's default port
EXPOSE 8001
EXPOSE 8002
ENV PYTHONUNBUFFERED 1
WORKDIR /root
RUN apt-get update
RUN apt-get update --fix-missing
RUN apt-get install apt-utils python3-pip python3-dev build-essential npm firefox curl git xvfb wget psmisc libpq-dev -y
RUN curl -sL https://deb.nodesource.com/setup_9.x | bash -
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
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
# RUN npm install
# RUN npm run build
RUN ln -s /app/dev_settings.json /settings.json
RUN ./manage.py collectstatic -v0 --noinput
RUN mv node_modules /root