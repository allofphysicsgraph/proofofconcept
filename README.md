
This repo is the source code for the website https://derivationmap.net/

The Physics Derivation Graph is a project focused on the following:
* Claim: a finite static directed graph exists which describes all of mathematical Physics. 
* Claim: the graph representation is machine parsable
* Claim: validity of derivation steps in the graph can be checked by a computer algebra system

Status as of Sept 2020: project author believes claim 1 and 2.
It is not clear to the project author that current computer algebra systems are capable of validating all of mathematical Physics.

A surprising outcome of this work has been the enumeration of [inference rules used in mathematical Physics](https://derivationmap.net/user_documentation#inference%20rules).

[![Join the chat at https://gitter.im/allofphysicsgraph/Lobby](https://badges.gitter.im/allofphysicsgraph/Lobby.svg)](https://gitter.im/allofphysicsgraph/Lobby)

# Goals / Objectives

- [x] Create a framework capable of describing all mathematics needed for physics derivations. I use Latex as the syntax in the framework because Latex is how I think of equations. However, Latex is insufficient for processing by computer algebra systems. Status: proof of concept exists
- [x] Create machine-readable databases which use the above framework to capture the mathematical derivations in physics. To hold the content of the databases I'm using custom XML. Status: proof of concept exists
- [x] Create graphical representation of relations content in the databases. I'm using d3js (previously GraphViz) to render the visualization. Status: proof of concept works
- [x] Use a computer algebra system to verify the relations in the databases. I'm using SymPy as the CAS. Status: proof-of-concept completed in 2020
- [x] Create a web browser-based viewing of the generated graph. HTML5 seems capable. Status: proof-of-concept completed in 2020
- [x] Create a web browser-based graph input tool. Status: proof-of-concept completed in 2020

The proof-of-concept for all objectives were completed during the Covid-19 lockdown (summer of 2020). The next steps are unclear. Adding content manually is burdensome. The website is not polished -- errors occur and the look is amateur. 

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

See [developer documentation](https://derivationmap.net/developer_documentation?referrer=github_README) after reading the [user documentation](https://derivationmap.net/user_documentation)

# a small derivation

![Physics derivation graph: integration by parts](https://derivationmap.net/static/derivation_000009_baa130c08a240e5ea9a5abe53425377d.png)
