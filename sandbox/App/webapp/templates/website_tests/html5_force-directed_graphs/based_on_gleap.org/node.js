/**
 * Name: node.js
 * Desc: Simple structure to contain basic information about 
 *       a node in the node|art project
**/

var DEFAULT_NODE_COLOR = "#A66411";
var NODE_RADIUS = 5;

function Node(x, y, id)
{
	this.x = x;
	this.y = y;
	this.id = id;
	this.color = DEFAULT_NODE_COLOR;
	this.edges = [];

	/**
	 * Name: draw(canvas)
	 * Desc: Draws this node on the provided canvas
	 * Para: context, The canvas context to draw this node with
	**/
	this.draw = function(context)
	{
		context.lineWidth = 0;
		context.fillStyle=this.color;
		context.beginPath();
		context.arc(this.x,this.y,NODE_RADIUS,0,Math.PI*2,true);
		context.closePath();
		context.fill();
	}

	/**
	 * Name: addEdge(edge)
	 * Desc: Informs this node that it is participating in the
	 *       connection described by the given edge
	 * Para: edge, The edge that connects this node to another
	 *             node
	**/
	this.addEdge = function(edge)
	{
		this.edges.push(edge);
	}

	/**
	 * Name: setX(newX)
	 * Desc: Sets the x position of this node to the given new value
	 * Para: newX, The new x value to give this node
	**/
	this.setX = function(newX)
	{
		this.x = newX;
	}

	/**
	 * Name: setY(newY)
	 * Desc: Sets the y position of this node to the given new value
	 * Para: newY, The new x value to give this node
	**/
	this.setY = function(newY)
	{
		this.y = newY;
	}

	/**
	 * Name: getX()
	 * Desc: Gets the current x value for this node
	 * Retr: The current numerical x position of this node
	**/
	this.getX = function()
	{
		return this.x;
	}

	/**
	 * Name: getY()
	 * Desc: Gets the current y value for this node
	 * Retr: The current numerical y position of this node
	**/
	this.getY = function()
	{
		return this.y;
	}

	/**
	 * Name: getY()
	 * Desc: Gets the numerical id for this node
	 * Retr: The id of this node
	**/
	this.getID = function()
	{
		return this.id;
	}

}