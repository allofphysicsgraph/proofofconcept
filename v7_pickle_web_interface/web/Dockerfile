# https://docs.docker.com/engine/reference/builder/#from
# https://github.com/phusion/baseimage-docker
FROM phusion/baseimage:0.11
# Ubuntu is too big 
#FROM ubuntu:latest

# https://docs.docker.com/engine/reference/builder/#run
RUN apt-get update && \
    apt-get install -y \
               vim \
               python3 \
               python3-pip \
               python3-dev \
#               python2.7 \
#               python-pip \
               build-essential  \
               graphviz \
               dvipng \
               git-core \
#               2to3 \
#               automake \
#               autoreconf \
               texlive \
    && rm -rf /var/lib/apt/lists/*

# https://docs.docker.com/engine/reference/builder/#copy
COPY requirements.txt /tmp

# not currently necessary, but may be useful in the future
#RUN git clone https://github.com/mathjax/MathJax.git MathJax

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
USER appuser

COPY templates     /home/appuser/app/templates
COPY static        /home/appuser/app/static
COPY controller.py /home/appuser/app
COPY compute.py    /home/appuser/app
COPY config.py     /home/appuser/app
COPY data.pkl      /home/appuser/app
COPY tests.sh      /home/appuser/app

USER root
RUN chown -R appuser /home/appuser/app && chgrp -R appuser /home/appuser/app
USER appuser

# An ENTRYPOINT allows you to configure a container that will run as an executable.
ENTRYPOINT ["python3"]

# There can only be one CMD instruction in a Dockerfile
# The CMD instruction should be used to run the software contained by your image, along with any arguments. 
CMD ["/home/appuser/app/controller.py"]

