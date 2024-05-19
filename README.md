
This repo is the source code for the website <https://derivationmap.net/>, aka <https://allofphysics.com>.

The Physics Derivation Graph focuses on the following:
* Claim: a finite static directed graph exists which describes all of mathematical Physics. 
* Claim: the graph representation is machine parsable
* Claim: validity of (some) derivation steps in the graph can be checked using a computer algebra system
* Claim: correctness of (some) derivation steps in the graph can be proven formally

As of May 2024 claims 1, 2, and 3 are demonsrated; work on 4 is planned.

Caveats:
* I'm not aware of currently available computer algebra systems are capable of validating all of mathematical Physics.
* The graph relies on manually checking the equivalence of expressions represented using Latex, Sympy, and Lean. 


A novel result of this work has been the enumeration of [inference rules used in mathematical Physics](https://derivationmap.net/user_documentation#inference%20rules).

[![Join the chat at https://gitter.im/allofphysicsgraph/Lobby](https://badges.gitter.im/allofphysicsgraph/Lobby.svg)](https://gitter.im/allofphysicsgraph/Lobby)

# Goals / Objectives

## Initial Objectives

- [x] Create a framework capable of describing all mathematics needed for physics derivations. PDG uses Latex as the syntax in the framework because Latex is how I think of equations. However, Latex is insufficient for processing by computer algebra systems. Status: proof of concept exists
- [x] Create machine-readable databases which use the above framework to capture the mathematical derivations in physics. To hold the content of the databases I'm using custom XML. Status: proof of concept exists
- [x] Create graphical representation of relations content in the databases. PDF uses d3js (previously GraphViz) to render the visualization. Status: proof of concept works
- [x] Use a computer algebra system to verify the relations in the databases. PDG uses SymPy as the CAS. Status: proof-of-concept completed in 2020
- [x] Create a web browser-based viewing of the generated graph. HTML5 seems capable. Status: proof-of-concept completed in 2020
- [x] Create a web browser-based graph input tool. Status: proof-of-concept completed in 2020

The proof-of-concept for all the initial objectives were completed during the Covid-19 lockdown (summer of 2020). 

## Current unmet objectives

- [ ] Use a property graph (e.g., Neo4j) and enable users to query the graph. Status: underway as of May 2024
- [ ] Adapt visualizations to the new property graph database
- [ ] Adding content manually is burdensome. Find automations
- [ ] Eliminate website errors
- [ ] Enact testing of the backend software and the web UI.


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

# Contributing

Before submitting code via a pull request, please open an issue (feature or bug) and describe your question or intent.

Python code is formatted using Black.


