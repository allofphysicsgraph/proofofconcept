/**
 * Name: edge.js
 * Desc: Contains Edge class that represents an edge between two nodes
**/

var DEFAULT_EDGE_COLOR = "#000000";

/**
 * Name: Edge(node1, node2)
 * Desc: Creates a new edge between node1 and node2
 * Para: node1, The first node in this edge
 *       node2, The second node in this edge
 *       applyToNodes, If true, the nodes are immediately
 *                     updated to show that they are in this
 *                     edge. If false, client code must
 *                     call addToNodes later
**/
function Edge(node1, node2, applyToNodes)
{
    this.node1 = node1;
    this.node2 = node2;
    this.color = DEFAULT_EDGE_COLOR;

    /**
     * Name: draw(canvas)
     * Desc: Draws this edge on the provided canvas
     * Para: context, The canvas context to draw this node with
    **/
    this.draw = function(context)
    {
        // Get positions
        var x1 = this.node1.getX();
        var x2 = this.node2.getX();
        var y1 = this.node1.getY();
        var y2 = this.node2.getY();

        // Actually draw
        context.lineWidth = 1;
        context.strokeStyle=this.color;
        context.moveTo(x1, y1);
        context.lineTo(x2, y2);
        context.stroke();
    }

    /**
     * Name: getNodes()
     * Desc: Gets the two nodes on this edge
     * Retr: List of two elements, each a Node instance
    **/
    this.getNodes = function()
    {
        return [this.node1, this.node2];
    }

    /**
     * Name: getOtherNode(node)
     * Desc: Gets the other node on this edge
     * Para: node, The node whose paired node on this edge is desired
     * Retr: Other node instance or null if the passed node was not
     *       on this edge
    **/
    this.getOtherNode = function(passedNode)
    {
        var edgeNodes = this.getNodes();

        if(edgeNodes[0].getID() == passedNode.getID())
        {
            return edgeNodes[1];
        }
        else if(edgeNodes[1].getID() == passedNode.getID())
        {
            return edgeNodes[0];
        }
        else
        {
            return null;
        }
    }

    /**
     * Name: addToNodes()
     * Desc: Informs the nodes of this edge that they
     *       are attached to this edge
    **/
    this.addToNodes = function()
    {
        this.node1.addEdge(this);
        this.node2.addEdge(this);
    }

    if(applyToNodes)
        this.addToNodes();
}