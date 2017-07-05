/**
 * Simmple graph layout system
 * http://processingjs.nihongoresources.com/graphs
 * (c) Mike "Pomax" Kamermans 2011
 */

/**
 * Trees are actually a subset of directed graphs,
 * in which there is always one, and only one, way to
 * get from one node to another node (i.e. they are
 * "loop free" directed graphs)
 */
class Tree extends DirectedGraph
{
  Node root;
  Tree(Node r) { 
    root = r; 
    nodes.add(root);
    flower = new TreeFlowAlgorithm(); }

  Node getRoot() { return root; }

  void addChild(Node parent, Node child) {
    nodes.add(child);
    linkNodes(parent, child); }
    
  int getDepth() { return getDepth(root); }
  
  int getDepth(Node r)
  {
    if(r.getOutgoingLinksCount()==0) return 1;
    int d = 0;
    ArrayList<Node> outgoing = r.getOutgoingLinks();
    for(Node child: outgoing) {
      int dc = getDepth(child);
      if(dc>d) { d=dc; }}
    return 1+d;
  }
}
