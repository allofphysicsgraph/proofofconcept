/**
 * Simmple graph layout system
 * http://processingjs.nihongoresources.com/graphs
 * (c) Mike "Pomax" Kamermans 2011
 */

// this is the interface for graph reflowing algorithms
interface FlowAlgorithm {
  // returns "true" if done, or "false" if not done
  boolean reflow(DirectedGraph g); }
