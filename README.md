
http://allofphysicsgraph.github.io/proofofconcept/


Physics Derivation Graph

* Claim: a finite static directed graph exists which describes all of mathematical physics. 
* Claim: the graph representation is machine parsable
* Claim: this graph can be checked by a computer algebra system

# Licensing
[Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/)



# Requirements

[Python 2.7](http://www.python.org/getit/)

Python packages: 
* yaml

Non-Python applications
* Latex
* [Graphviz](http://www.graphviz.org/) (neato)

# How to use (for the impatient)

main commands:

    cd v3_csv  
    python bin/create_picture_per_derivation_from_connectionsDB.py

tools

    python bin/list_derivations.sh
    python bin/list_inference_rules.py

statistical analysis

    python bin/popularity_of_inference_rules.py
    python bin/popularity_of_expressions.py
    python bin/popularity_of_symbols.py

validate connections

    python bin/check_connections_using_CAS.py



Command:

    python bin/build_connections_graph.py

output: two pictures, each showing the graph for the selected sequence
* "out_no_labels.png"
* "out_with_labels.png"

These were generated using GraphViz and the output file
"connection_result.gv"
and the command 

    neato -Tpng connections_result.gv > out_with_labels.png

The other two output files are the same graph,
"connections_result.py"
for use with Networkx
"connections_result.graphml"
for input to graph plotting programs like yED


# Status

Development and testing performed on Mac OS 10.11.2

Currently, content is entered into CSV files:
* connections_database.csv: relation between inference rules and expressions
** one inference rule per step (for Latex generation)
* expressions_database.csv  : library of unique expressions used by connections
* inference_rules_database.csv  : library of unique inference rules used by connections
* comments_database.xml   : set of comments which may reference multiple expressions or steps



doc/physics_graph_notes.log: my commentary and observations on the project as it progresses

