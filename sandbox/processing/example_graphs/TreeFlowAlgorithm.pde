/**
 * Simmple graph layout system
 * http://processingjs.nihongoresources.com/graphs
 * (c) Mike "Pomax" Kamermans 2011
 */

/**
 * Flow algorithm for trees - only works for Trees
 */
class TreeFlowAlgorithm implements FlowAlgorithm
{
  boolean reflow(DirectedGraph g)
  {
    if(g instanceof Tree) { 
      Tree t = (Tree) g;
      int depth = t.getDepth();
      int vstep = (height-20)/depth;
      int vpos = 30;

      Node first = t.root;
      first.x = width/2;
      first.y = vpos;
      
      // breadth-first iteration
      ArrayList<Node> children = t.root.getOutgoingLinks();
      while(children.size()>0)
      {
        vpos += vstep;
        int cnum = children.size();
        int hstep = (width-20) / cnum;
        int hpos = 10 + (hstep/2);
        ArrayList<Node> newnodes = new ArrayList<Node>();
        for(Node child: children) {
          child.x = hpos;
          child.y = vpos;
          addAll(newnodes, child.getOutgoingLinks());
          hpos += hstep;
        }
        children = newnodes;
      }
    }
    return true;
  }
}
