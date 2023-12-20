- author: Ben Payne
- project: Physics Derivation Graph
- website: https://allofphysics.com

# Quickstart

To start the containers, run
```bash
docker kill $(docker ps -q); make up
```
and then, in a web browser, go to <http://localhost:5000>

Because software is in Docker containers (for reproducibility), the versions of the Docker software you're using matter. The software in this repo has been tested with
* docker-compose 1.29.2
* Compose file format 3.6
* Docker Engine release 20.10.11
See <https://docs.docker.com/compose/compose-file/compose-versioning/> for compatibility of versions.

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
