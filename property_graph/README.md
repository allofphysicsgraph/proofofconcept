
Two containers: Neo4j (port 7474) and a flask web server (port 5000)



# CYPHER queries cheat sheet

all nodes:
```
MATCH (n) RETURN n
```
all edges:
```
MATCH (n)-[r]->(m) RETURN n,r,m
```

