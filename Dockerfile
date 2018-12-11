# 20180602

FROM python:2.7-alpine

MAINTAINER My Name <my.email.address@gmail.com>

LABEL distro_style="apk" distro="alpine" arch="x86_64" operatingsystem="linux"

RUN apk add --update --no-cache graphviz
RUN apk add --update --no-cache texlive-full
RUN apk add --update --no-cache texlive

RUN pip install pyyaml
RUN pip install sympy

RUN mkdir /derivations
RUN mkdir /inference_rules

#RUN apk add --no-cache curl
#RUN git clone https://github.com/allofphysicsgraph/proofofconcept.git

ADD v4_file_per_expression/interactive_user_prompt.py interactive_user_prompt.py
ADD lib/lib_physics_graph.py /lib/lib_physics_graph.py
ADD v4_file_per_expression/inference_rules/* /inference_rules/

#WORKDIR /bin

CMD ["python", "interactive_user_prompt.py"]
