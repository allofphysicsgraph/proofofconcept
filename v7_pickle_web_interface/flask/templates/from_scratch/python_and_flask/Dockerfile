# Physics Derivation Graph
# Ben Payne, 2020
# https://creativecommons.org/licenses/by/4.0/
# Attribution 4.0 International (CC BY 4.0)


# https://docs.docker.com/engine/reference/builder/#from
# https://github.com/phusion/baseimage-docker
FROM phusion/baseimage:0.11

# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disk (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE 1

# https://docs.docker.com/engine/reference/builder/#run
RUN apt-get update && \
    apt-get install -y \
               python3 \
               python3-pip \
               python3-dev \
    && rm -rf /var/lib/apt/lists/*

# https://docs.docker.com/engine/reference/builder/#copy
# requirements.txt contains a list of the Python packages needed for the PDG
COPY requirements.txt /tmp

RUN pip3 install -r /tmp/requirements.txt

COPY controller.py /opt/

# There can only be one CMD instruction in a Dockerfile
# The CMD instruction should be used to run the software contained by your image, along with any arguments. 
CMD ["/opt/controller.py"]

