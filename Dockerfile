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
RUN apt-get update --fix-missing
RUN apt-get install --no-install-recommends python3-venv python3-pip python3.8 python3.8-dev build-essential npm curl git wget postgresql-client psmisc libpq-dev -y
RUN apt-get upgrade -y
RUN apt-get autoremove -y
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get install -y nodejs
RUN /usr/bin/python3.8 -m pip install --upgrade pip
RUN /usr/bin/python3.8 -m pip install --upgrade virtualenv
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 10
RUN mkdir /app
RUN mkdir /home/dev
RUN groupadd -g 1000 dev
RUN useradd -u 1000 -d /home/dev -g dev dev
RUN chown -R 1000:1000 /app
RUN chown -R 1000:1000 /home/dev
USER 1000
WORKDIR /home/dev
# Master at the time of coding.
RUN curl -L https://github.com/pyenv/pyenv-installer/raw/6f1a69aaa56ead1c584699d0d5a426ecf74f560d/bin/pyenv-installer | bash
RUN echo 'eval "$(pyenv virtualenv-init -)"' > .bashrc
ENV LANG=C.UTF-8
ENV HOME  /home/dev
ENV PYENV_ROOT $HOME/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH;$HOME/.local/bin
WORKDIR /app
ADD . .
RUN pyenv virtualenv system artconomy
RUN echo artconomy > /app/.python-version
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# More modificiations need to be done to this dockerfile to make it production-ready. Right now containers aren't
# used for deployment, only dev.
