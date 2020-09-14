
This repo is the source code for the website https://derivationmap.net/

The Physics Derivation Graph is a project focused on the following:
* Claim: a finite static directed graph exists which describes all of mathematical Physics. 
* Claim: the graph representation is machine parsable
* Claim: validity of derivation steps in the graph can be checked by a computer algebra system

Status as of Sept 2020: project author believes claim 1 and 2.
It is not clear to the project author that current computer algebra systems are capable of validating all of mathematical Physics.

A surprising outcome of this work has been the enumeration of [inference rules used in mathematical Physics](https://derivationmap.net/user_documentation#inference%20rules).

[![Join the chat at https://gitter.im/allofphysicsgraph/autoproof](https://badges.gitter.im/allofphysicsgraph/autoproof.svg)](https://gitter.im/allofphysicsgraph/autoproof?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

# Licensing


[Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/)

# Software Requirements

* Docker
* a web browser

# How to use (for the impatient)

    git clone https://github.com/allofphysicsgraph/proofofconcept.git
    cd proofofconcept/v7_pickle_web_interface/flask/
    docker build -t flask_ub .
    docker run -it --rm -v`pwd`/data.json:/home/appuser/app/data.json \
               -v`pwd`/logs/:/home/appuser/app/logs/ \
               --publish 5000:5000 flask_ub


# a small derivation

![Physics derivation graph: integration by parts](https://derivationmap.net/static/derivation_000009_baa130c08a240e5ea9a5abe53425377d.png)
