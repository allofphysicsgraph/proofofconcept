import networkx as nx
# https://trac.macports.org/ticket/31891
import sys
sys.path.reverse()
import matplotlib.pyplot as plt

# http://networkx.lanl.gov/tutorial/tutorial.html
# http://networkx.lanl.gov/reference/classes.digraph.html
G = nx.DiGraph()
G.add_node(1)
G.add_node(2)
G.add_node(3)
G.add_node(4)
G.add_edge(1,2)
G.add_edge(3,4)
G.add_edge(1,4)
nx.draw(G)
plt.show()