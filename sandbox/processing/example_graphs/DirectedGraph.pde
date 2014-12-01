/**
 * Simmple graph layout system
 * http://processingjs.nihongoresources.com/graphs
 * (c) Mike "Pomax" Kamermans 2011
 */

// this class models a directed graph, consisting of any number of nodes
class DirectedGraph
{
  ArrayList<Node> nodes = new ArrayList<Node>();
  FlowAlgorithm flower = new CircleFlowAlgorithm();
  
  void setFlowAlgorithm(FlowAlgorithm f) {
    flower = f; }

  void addNode(Node node) {
    if(!nodes.contains(node)) {
      nodes.add(node); }}

  int size() { return nodes.size(); }

  boolean linkNodes(Node n1, Node n2) {
    if(nodes.contains(n1) && nodes.contains(n2)) {
      n1.addOutgoingLink(n2);
      n2.addIncomingLink(n1); 
      return true; }
    return false; }

  Node getNode(int index) {
    return nodes.get(index); }

  ArrayList<Node> getNodes() {
    return nodes; }

  ArrayList<Node> getRoots() {
    ArrayList<Node> roots = new ArrayList<Node>();
    for(Node n: nodes) {
      if(n.getIncomingLinksCount()==0) {
        roots.add(n); }}
    return roots; }

  ArrayList<Node> getLeaves() {
    ArrayList<Node> leaves = new ArrayList<Node>();
    for(Node n: nodes) {
      if(n.getOutgoingLinksCount()==0) {
        leaves.add(n); }}
    return leaves; }

  // the method most people will care about
  boolean reflow() { return flower.reflow(this); }
  
  // this does nothing other than tell nodes to draw themselves.
  void draw() {
    for(Node n: nodes) {
      n.draw(); }}
}