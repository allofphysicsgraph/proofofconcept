
http://allofphysicsgraph.github.io/proofofconcept/


Physics Derivation Graph

* Claim: a finite static directed graph exists which describes all of mathematical physics. 
* Claim: the graph representation is machine parsable
* Claim: this graph can be checked by a computer algebra system

# Licensing
Creative Commons Attribution-ShareAlike 3.0 Unported License.

# Requirements

Python 2.7, http://www.python.org/getit/

Python packages: 
* yaml
* xml.dom.minidom

Non-Python applications
* Latex
* Graphviz (neato), http://www.graphviz.org/

# How to use (for the impatient)

main commands:

    python bin/create_pictures_of_statements_and_grammar.py
    python bin/build_connections_graph.py

tools

    python bin/list_connection_sets.py
    python bin/list_inference_rules.py
    python bin/generate_new_random_index.py

statistical analysis

    python bin/popularity_of_inference_rules.py
    python bin/popularity_of_statements.py
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

Development and testing performed on Mac OS 10.7.5

Currently, content is manually coded into XML files:
* connections_database.csv: how do inference rules and statements relate?
** assumption: order of steps within a derivation matters (for Latex generation)
** assumption: one inference rule per step (for Latex generation)
* expressions_database.csv  : library of unique expressions used by connections
* inference_rules_database.csv  : library of unique inference rules used by connections
* comments_database.xml   : set of comments which may reference multiple expressions or steps



physics_graph_notes.log: my commentary and observations on the project as it progresses

