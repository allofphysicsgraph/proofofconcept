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
#               python2.7 \
#               python-pip \
# documentation generation
               python3-sphinx \
               build-essential  \
# generate pictures of graphs using dot
               graphviz \
# generate pictures of expressions using latex
               dvipng \
#               git-core \
# npm for mathjax
               npm \
#               2to3 \
#               automake \
#               autoreconf \
# compile .tex to .dvi
               texlive \
    && rm -rf /var/lib/apt/lists/*

# https://docs.docker.com/engine/reference/builder/#copy
# requirements.txt contains a list of the Python packages needed for the PDG
COPY requirements.txt /tmp

# https://www.npmjs.com/package/mathjax
RUN npm install mathjax@3

# convert DVI to SVG
# not necessary, and written in Python2. Conversion to Python3 using 2to3 failed :(
#RUN git clone https://github.com/WojciechMula/pydvi2svg.git
#RUN ln -sf /app/pydvi2svg/dvi2svg.py /usr/local/bin/
#RUN cat pydvi2svg/dvi2png.py | sed 's/#!\/usr\/bin\/python/\/usr\/bin\/python3/' > pydvi2svg/dvi2png.py
#RUN cat pydvi2svg/conv/binfile.py | sed 's/binfile(file/binfile(filename/' > pydvi2svg/conv/binfile.py
#RUN git clone https://github.com/fontforge/fontforge.git
#RUN git clone https://github.com/fontforge/libspiro.git
#RUN git clone https://github.com/fontforge/libuninameslist.git

RUN pip3 install -r /tmp/requirements.txt

RUN useradd --create-home appuser
WORKDIR /home/appuser/app
RUN mkdir -p       /home/appuser/app/uploads
USER appuser

COPY templates     /home/appuser/app/templates
COPY static        /home/appuser/app/static
COPY common_lib.py \
     compute.py \
     config.py \
     controller.py \
     json_schema.py \
     Makefile \
     pdg_api.py \
     validate_inference_rules_sympy.py \
     wsgi.py \
     /home/appuser/app/

USER root
RUN mv /node_modules/mathjax/es5 /home/appuser/app/static/mathjax
RUN chown -R appuser /home/appuser/app && chgrp -R appuser /home/appuser/app

# TODO - https://github.com/allofphysicsgraph/proofofconcept/issues/82
#RUN tlmgr init-usertree
#RUN apt-get install -y texlive-base
#RUN apt-get install -y wget xzdec
#RUN /usr/bin/tlmgr install braket
USER appuser
RUN echo "alias python=python3" > /home/appuser/.bashrc
RUN bash -l /home/appuser/.bashrc

# An ENTRYPOINT allows you to configure a container that will run as an executable.
ENTRYPOINT ["python3"]

# There can only be one CMD instruction in a Dockerfile
# The CMD instruction should be used to run the software contained by your image, along with any arguments. 
CMD ["/home/appuser/app/controller.py"]

