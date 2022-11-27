- author: Ben Payne
- project: Physics Derivation Graph
- website: https://allofphysics.com

# Quickstart

To start the containers, run
```bash
make up
```
and then, in a web browser, go to <http://localhost:5000>

# Project contents
Two containers: Neo4j (port 7474) and a flask web server (port 5000)

# Neo4j for newbies

A graph has "nodes" and "edges". A property graph extends that
data structure to allow "properties" for both the nodes and the edges.

Nodes and edges in Neo4j are described using the following jargon:

    :label {key1:'value1', key2:'value2'}

where the key-value pairs are properties. The schema is effectively the labels and keys for edges and nodes.

"Node labels, relationship types, and properties (the key part) are case sensitive." (citation)[https://neo4j.com/docs/getting-started/current/appendix/graphdb-concepts/]

# Aspirational web interface:
<http://www.apcjones.com/arrows/> and <https://arrows.app/>
