import networkx as nx
# https://trac.macports.org/ticket/31891
import sys
sys.path.reverse()
import matplotlib.pyplot as plt

# http://networkx.lanl.gov/tutorial/tutorial.html
# http://networkx.lanl.gov/reference/classes.digraph.html
G = nx.DiGraph()

#    <connection>
#       <operator><op_name>multbothsidesby</op_name>           <label>6822583</label></operator>
#       <input>   <feed>f</feed>                               <label>5749291</label></input>
#       <input>   <statement_index>3131111133</statement_index><label>8482459</label></input>
#       <output>  <statement_index>2131616531</statement_index><label>8341200</label></output>
#    </connection>   

#  These lables aren't used 
# labl={}
# G.add_node(5224)
# labl[0]='multbothsidesby'
# G.add_node(9532)
# labl[1]='$T=1/f$'
# G.nodes(data=True)
# nx.draw(G,node_label=labl)
# plt.show()

#  These lables aren't used 
# G.add_node(5224,labl='multbothsidesby')
# G.add_node(9532,labl='$T=1/f$')
# G.nodes(data=True)
# nx.draw(G,node_label=labl)
# plt.show()

G.add_node(5224,node_label='multbothsidesby')
G.add_node(9532,node_label='$T=1/f$')
G.nodes(data=True)
nx.draw(G)
plt.show()

# The following doesn't work, although labels are displayed correctly
# G.add_node('multbothsidesby')
# G.add_node('multbothsidesby')
# G.add_node('$\omega=2 \pi f$')
# G.add_node('$T=1/f$')
# G.add_node('$T\ f=1$')
# G.add_node('$f$')
# G.add_edge('$f$','multbothsidesby')
# G.add_edge('$T=1/f$','multbothsidesby')
# G.add_edge('multbothsidesby','$T\ f=1$')
# nx.draw(G)
# plt.show()

#    <connection>
#       <operator><op_name>multbothsidesby</op_name>           <label>9483715</label></operator>
#       <input>   <feed>T</feed>                               <label>8837284</label></input>
#       <input>   <statement_index>2131616531</statement_index><label>8341200</label></input>
#       <output>  <statement_index>2113211456</statement_index><label>9380032</label></output>
#    </connection>   
#    <connection>
#       <operator><op_name>subRHSofEqXintoEqY</op_name>        <label>9483843</label></operator>
#       <input>   <statement_index>2113211456</statement_index><label>9380032</label></input>
#       <input>   <statement_index>3131211131</statement_index><label>0921465</label></input>
#       <output>  <statement_index>3132131132</statement_index><label>8374556</label></output>
#    </connection>   
