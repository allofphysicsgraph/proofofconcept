# https://docs.docker.com/engine/reference/builder/#from
# https://github.com/phusion/baseimage-docker
FROM phusion/baseimage:0.11
# Ubuntu is too big 
#FROM ubuntu:latest

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
               build-essential  \
               graphviz \
    && rm -rf /var/lib/apt/lists/*

# https://docs.docker.com/engine/reference/builder/#copy
# requirements.txt contains a list of the Python packages needed for the PDG
COPY requirements.txt /tmp

RUN pip3 install -r /tmp/requirements.txt

COPY ast_test.py /opt/ 


