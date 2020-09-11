
See http://allofphysicsgraph.github.io/proofofconcept/
 for visualizations of the content


project name: Physics Derivation Graph

* Claim: a finite static directed graph exists which describes all of mathematical physics. 
* Claim: the graph representation is machine parsable
* Claim: this graph can be checked by a computer algebra system

# Licensing

[![Join the chat at https://gitter.im/allofphysicsgraph/autoproof](https://badges.gitter.im/allofphysicsgraph/autoproof.svg)](https://gitter.im/allofphysicsgraph/autoproof?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) [![Join the chat at https://gitter.im/allofphysicsgraph/proofs](https://badges.gitter.im/allofphysicsgraph/proofs.svg)](https://gitter.im/allofphysicsgraph/proofs?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

[Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/)



# Requirements

* Docker
* a web browser

# How to use (for the impatient)

Using 
https://github.com/allofphysicsgraph/proofofconcept/blob/gh-pages/v7_pickle_web_interface/web/Dockerfile

    python create_tmp_db.py ; docker build -t flask_ub .; docker run -it --rm --publish 5000:5000 flask_ub


# Status

In active development as of 20200315

# a small derivation

![Physics derivation graph: integration by parts](https://allofphysicsgraph.github.io/proofofconcept/site/pictures/generated_from_project/graph_integration_by_parts_without_labels.png)
