# Physics Derivation Graph
# Ben Payne, 2021
# https://creativecommons.org/licenses/by/4.0/
# Attribution 4.0 International (CC BY 4.0)


# https://docs.docker.com/engine/reference/builder/#from
# https://github.com/phusion/baseimage-docker
FROM phusion/baseimage:focal-1.1.0

WORKDIR /code
ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0

# since I'm not using python:3.7, I have to install Python
# from https://github.com/Docker-Hub-frolvlad/docker-alpine-python3/blob/master/Dockerfile
# This hack is widely applied to avoid python printing issues in docker containers.
# See: https://github.com/Docker-Hub-frolvlad/docker-alpine-python3/pull/13
ENV PYTHONUNBUFFERED=1

# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disk (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE 1

# https://docs.docker.com/engine/reference/builder/#run
RUN apt-get update && \
    apt-get install -y \
# text editing
               vim \
               python3 \
               python3-pip \
               python3-dev \ 
# documentation generation
               python3-sphinx \
# generate pictures of graphs using dot
               graphviz \
# generate pictures of expressions using latex
               dvipng \
# npm for mathjax
               npm \
# compile .tex to .dvi
               texlive   && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi

# https://www.npmjs.com/package/mathjax
RUN npm install mathjax@3
#RUN npm install mathjax

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# TODO: don't be root!

RUN mkdir -p /code/static/mathjax
RUN mv /code/node_modules/mathjax/es5 /code/static/mathjax

EXPOSE 5000
COPY . .

CMD ["flask", "run"]
