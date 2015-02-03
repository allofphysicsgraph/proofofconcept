/**
 * Name: graph_manager.js
 * Desc: A facade that manages a collection of nodes and edges in
 *       the node|art project, calculating thier positions and
 *       running Djikstra's algorithm on them
**/

/**
 * Name: GraphManager(numNodes, minX, minY, maxX, maxY)
 * Desc: Creates a new Manager with a set of numNodes in 
 *       random positions
 * Para: numNodes, The number of nodes to create
 *       numEdges, The number of edges to create
 *       minX, The minimum x value of new nodes
 *       minY, The minimum y value of new nodes
 *       maxX, The maximum x value of new nodes
 *       maxY, The maximum y value of new nodes
**/
function GraphManager(numNodes, numEdges, minX, minY, maxX, maxY)
{
    this.nodes = []; // Kinda inefficient
    this.edges = []; // Kinda inefficient
    this.minX = minX;
    this.minY = minY;
    this.maxX = maxX;
    this.maxY = maxY;
    this.forcedecoRatedNodes = []; // Kinda inefficient
    this.forcedecoRatedEdges = []; // Kinda inefficient
    this.nextNodeID = 0;

    /**
     * Name: getNextNodeID()
     * Desc: Determines what the id of the next node to
     *       add should be
     * Retr: Expected ID of the next node to be added
    **/
    this.getNextNodeID = function()
    {
        return this.nextNodeID;
    }

    /**
     * Name: getNumNodes()
     * Desc: Determines the number of nodes in this manager
     * Retr: Number of nodes in the manager
    **/
    this.getNumNodes = function()
    {
        return this.nodes.length;
    }

    /**
     * Name: addNode(newNode)
     * Desc: Adds a new node to this node manager
     * Para: newNode, The new node to add to this manager
    **/
    this.addNode = function(newNode)
    {
        this.nextNodeID++;
        this.nodes[newNode.getID()] = newNode;
        this.forcedecoRatedNodes.push(new ForceNodeDecorator(newNode));
    }

    /**
     * Name: addEdge(newEdge)
     * Desc: Adds a new edge to this node manager
     * Para: newNode, The new edge to add to this manager
    **/
    this.addEdge = function(newEdge)
    {
        this.edges.push(newEdge);
        this.forcedecoRatedEdges.push(new ForceEdgeDecorator(newEdge));
    }

    /**
     * Name: getNode(id)
     * Desc: Gets the node managed by this manager with the
     *       given ID
     * Para: id, The id of the desired node
     * Retr: Node instance or null if not managed by this manager
    **/
    this.getNode = function(id)
    {
        if(id < 0 || id > this.nodes.length)
            return null;
        else
            return this.nodes[id];
    }

    /**
     * Name: highlightSpanningTree(startNode)
     * Desc: Use a modified version of Prim's algorithm to
     *       highlight the minimum spanning tree out of
     *       the provided startNode
     * Para: startNode, The node to start Prim's on
    **/
    this.highlightSpanningTree = function(startNode)
    {
        var primHeap = new PrimBinaryHeap();
        var tree = [];
        var currentNode;
        var previousNode;
        
        // Get the starting node and set its distance to zero
        tree.push(new PrimNodeDecorator(startNode, 0));
        primHeap.updateIfSmaller(startNode.getPrimNeighbors());

        // Construct tree of nodes and highlight
        while(!primHeap.empty())
        {
            currentNode = primHeap.pop();
            primHeap.updateIfSmaller(startNode.getPrimNeighbors());
            currentNode.highlight();
        }
    }

    /**
     * Name: updateGraph()
     * Desc: Take a step in the force based graph
     *       visualization algorithm
     * Para: deltaTime, Time in s since last iteration
     * Retr: The sum of the norms of the acceleration vectors
     *       of the nodes in this graph
    **/
    this.updateGraphConfiguration = function(deltaTime)
    {
        var totalAcceleration;
        var i;
        var j;
        var currentNode;
        var edgeNodes;
        var currentNodeID;
        var otherNodeID;
        var currentEdge;
        var otherNode;
        var numNodes = this.nodes.length;
        var numEdges = this.edges.length;
        var acceleration;
        var firstSpringForce;
        var secondSpringForce;

        // Reset forces on nodes
        for(i=0; i<numNodes; i++)
            this.forcedecoRatedNodes[i].clearForces();

        // Find new positions
        totalAcceleration = 0;

        // Handle charge forces
        for(i=0; i<numNodes; i++)
        {
            currentNode = this.forcedecoRatedNodes[i];

            // Calcuate the columb repulsion with all
            // OTHER nodes (hence first if stmt)
            for(j = i+1; j<numNodes; j++)
            {   
                // Get the other node
                otherNode = this.forcedecoRatedNodes[j];

                // Calculate repulsive force
                repulsiveForce = currentNode.calcCoulomb(otherNode);
                otherRepulsiveForce = repulsiveForce.generateOpposing();

                // Apply forces to both
                currentNode.addForce(repulsiveForce);
                otherNode.addForce(otherRepulsiveForce);
            }
        }

        // Handle spring forces
        for(i=0; i<numEdges; i++)
        {
            // Get edge
            currentEdge = this.forcedecoRatedEdges[i];

            // Get nodes
            edgeNodes = currentEdge.getNodes();
            currentNodeID = edgeNodes[0].getID();
            currentNode = this.forcedecoRatedNodes[currentNodeID];
            otherNodeID = edgeNodes[1].getID();
            otherNode = this.forcedecoRatedNodes[otherNodeID];

            // Calculate and apply force to first node
            firstSpringForce = currentEdge.calcHooke(currentNode, otherNode);
            currentNode.addForce(firstSpringForce);

            // Calculate and apply the other force
            secondSpringForce = firstSpringForce.generateOpposing();
            otherNode.addForce(secondSpringForce);
        }

        // Calculate new positions
        for(i = 0; i<numNodes; i++)
        {
            acceleration = this.forcedecoRatedNodes[i].update(deltaTime, 
                            this.minX, this.minY, this.maxX, this.maxY);
            totalAcceleration += acceleration.getMagnitude();
        }
        
        return totalAcceleration;
    }

    /**
     * Name: drawGraph(context)
     * Desc: Draws all the nodes and edges in this manager
     *       to the given context
     * Para: context, The context to draw the elements to
    **/
    this.drawGraph = function(context)
    {
        var i = 0;
        for(i = 0; i<this.edges.length; i++)
        {
            this.edges[i].draw(context);
        }

        for(i=0; i<this.nodes.length; i++)
        {
            this.nodes[i].draw(context);
        }
    }

    /**
     * Name: createGraph(numNodes, minX, minY, maxX, maxY)
     * Desc: Creates a new set of numNodes in random positions to 
     *       start this manager
     * Para: numNodes, The number of nodes to create
     *       numEdges, The number of edges to create
     *       minX, The minimum x value of new nodes
     *       minY, The minimum y value of new nodes
     *       maxX, The maximum x value of new nodes
     *       maxY, The maximum y value of new nodes
    **/
    this.createGraph = function(numNodes, numEdges, minX, minY, maxX, maxY)
    {
        var i = 0;
        var j = 0;
        var possibleEdges = []; // TODO: Initial size (numNodes choose 2)
        var node1;
        var node2;
        var newX;
        var newY;
        var edgeIndex;
        var edgeNodes;
        var previousPositions = {}; // Record of if a position was previously used
        var positionEncoding;

        // Build nodes
        for(i=0; i<numNodes;)
        {
            newX = randInt(minX, maxX);
            newY = randInt(minY, maxY);

            // Check to make sure x and y not already used
            positionEncoding = sprintf("%d,%d", newX, newY);
            if(previousPositions[positionEncoding] == undefined)
            {
                this.addNode(new Node(newX, newY, this.getNextNodeID()));
                previousPositions[positionEncoding] = true;
                i++;
            }
        }

        // Build list of all possible edges
        for(i=0; i<numNodes; i++)
        {
            for(j=i+1; j<numNodes; j++)
            {
                node1 = this.getNode(i);
                node2 = this.getNode(j);
                possibleEdges.push(new Edge(node1, node2, false));
            }
        }

        // Randomly select from those edges
        for(i=0; i<numEdges; i++)
        {
            edgeIndex = randInt(0, possibleEdges.length);
            edge = possibleEdges[edgeIndex];
            possibleEdges.remove(edgeIndex); // TODO: Pretty inefficient

            this.addEdge(edge);

            edge.addToNodes();
        }
    }

    this.createGraph(numNodes, numEdges, minX, minY, maxX, maxY);   
}