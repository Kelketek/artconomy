# specify the node base image with your desired version node:<version>
FROM ubuntu
# replace this with your application's default port
EXPOSE 8001
EXPOSE 8002
ENV PYTHONUNBUFFERED 1
WORKDIR /root
RUN apt-get update
RUN apt-get install apt-utils python3-pip python3-dev build-essential npm firefox curl git -y
RUN curl -sL https://deb.nodesource.com/setup_9.x | bash -
RUN apt-get install -y nodejs
RUN mkdir /app
WORKDIR /app
ADD . .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN npm install
RUN npm run build
RUN ln -s /app/dev_settings.json /settings.json
RUN ./manage.py collectstatic -v0 --noinput
RUN mv node_modules /root