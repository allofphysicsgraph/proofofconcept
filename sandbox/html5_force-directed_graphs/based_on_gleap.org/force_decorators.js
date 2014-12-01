/**
 * Name: force_decorators.js
 * Desc: Contains decorators around normal nodes and edges that
 *       calculate or aid in the calculation of velocities and
 *       positions based upon net forces
**/

var NODE_MASS = 1;
var SPRING_CONSTANT = 0.0001;
var NODE_CHARGE = 800;
var DAMPING = 0.90;
var MAX_VELOCITY = 100;
var MIN_DISTANCE = 10;
var SPRING_OFFSET = 1;
var BOUNCE_CONSTANT = 0;
var WALLS = true;

/**
 * Name: ForceNodeDecorator(x, y, id)
 * Desc: Creates a new force node around the given
 *       node to temporarily provide new basic
 *       physics methods to it
 * Para: innerNode, the node to decorate
**/
function ForceNodeDecorator(innerNode)
{
    this.innerNode = innerNode;
    this.forces = [];
    this.mass = NODE_MASS;
    this.velocity = new Vector(0, 0);

    /**
     * Name: getX()
     * Desc: Gets the current x value for this node
     * Retr: The current numerical x position of this node
    **/
    this.getX = function()
    {
        return this.innerNode.getX();
    }

    /**
     * Name: getY()
     * Desc: Gets the current y value for this node
     * Retr: The current numerical y position of this node
    **/
    this.getY = function()
    {
        return this.innerNode.getY();
    }

    /**
     * Name: getMass()
     * Desc: Determines the mass of this node
     * Retr: Mass of this node (number)
    **/
    this.getMass = function()
    {
        return this.mass;
    }

    /**
     * Name: calcCoulomb(otherNode)
     * Desc: Calculates the repulsive forces between
     *       two nodes, modeling that force off of
     *       coulomb's law
     * Retr: Vector instance as acting on this node
    **/
    this.calcCoulomb = function(otherNode)
    {
        var thisForce;
        var otherForce;
        var deltaX = this.getX() - otherNode.getX();
        var deltaY = this.getY() - otherNode.getY();
        var xComponent;
        var yComponent;
        var xDifference;
        var yDifference;
        var common;
        var distSquared;

        // TODO: Repeat calculations!
        distSquared = Math.pow(deltaX, 2) + Math.pow(deltaY, 2);
        if (distSquared >= MIN_DISTANCE)
            common = SPRING_CONSTANT * Math.pow(NODE_CHARGE / distSquared, 3/2);
        else 
            common = SPRING_CONSTANT * Math.pow(NODE_CHARGE / MIN_DISTANCE, 3/2);
        xComponent = deltaX * common;
        yComponent = deltaY * common;

        return new Vector(xComponent, yComponent);
    }

    /**
     * Name: calcSquaredDistance(otherNode)
     * Desc: Determines the squared distance between this
     *       node and the other node provided
     * Para: otherNode, the node to calculate
     *                  find this node's distance
     *                  from
     * Retr: Numerical distanace (scalar) between
     *       this node and the other node squared
    **/
    this.calcSquaredDistance = function(otherNode)
    {
        var deltaX = this.getX() - otherNode.getX();
        var deltaY = this.getY() - otherNode.getY();

        return Math.pow(deltaX, 2) + Math.pow(deltaY, 2);
    }

    /**
     * Name: calcDistance(otherNode)
     * Desc: Determines the distance between this
     *       node and the other node provided
     * Para: otherNode, the node to calculate
     *                  find this node's distance
     *                  from
     * Retr: Numerical distanace (scalar) between
     *       this node and the other node
    **/
    this.calcDistance = function(otherNode)
    {
        return Math.sqrt(this.calcSquaredDistance(otherNode));
    }

    /**
     * Name: calcAngle(otherNode)
     * Desc: Finds the angle (rad) between this node
     *       and the other node provided where 0 rad
     *       is due right and angle increases counter-
     *       clockwise
     * Para: otherNode, the other node to find the angle
     *                  between
    **/
    this.calcAngle = function(other)
    { 
        return Math.atan2(other.getY() - this.getY(), other.getX() - this.getX());
    }

    /**
     * Name: addForce(newForce)
     * Desc: Adds a new force to this node
     * Para: newForce, the new force (Vector) acting on this node
    **/
    this.addForce = function(newForce)
    {
        this.forces.push(newForce);
    }

    /**
     * Name: clearForces()
     * Desc: Clears all of the forces acting on this node
    **/
    this.clearForces = function()
    {
        this.forces = [];
    }

    /**
     * Name: getAcceleration()
     * Desc: get the current acceleration of this node
     * Retr: Vector representing the acceleration of this node
    **/
    this.getAcceleration = function()
    {
        var sumForces;
        var acceleration;
        var i = 0;
        var numForces = this.forces.length;

        // Calculate sum of forces
        sumForces = new Vector(0, 0);
        for(i = 0; i < numForces; i++)
        {
            sumForces = sumForces.add(this.forces[i]);
        }

        // Calculate acceleration
        acceleration = sumForces.multiplyConstant(this.getMass());

        return acceleration;
    }

    /**
     * Name: update(deltaTime)
     * Desc: Updates the position of this node by virtue of the
     *       sum of the forces on it
     * Para: deltaTime, the amount of time (s) after the current
     *                  state of this node that should be calculated
     *       minX, The minimum x value nodes can have
     *       minY, The minimum y value nodes can have
     *       maxX, The maximum x value nodes can have
     *       maxY, The maximum y value nodes can have
     * Retr: The acceleration (Vector) calculated for this node during the
     *       interval
    **/
    this.update = function(deltaTime, minX, minY, maxX, maxY)
    {
        var acceleration = this.getAcceleration();
        var halfDeltaTimeSquared = Math.pow(deltaTime, 2) / 2;
        var displacement;
        var newX;
        var newY;
        var deltaVelocity;
        var velocityMagnitue;

        // Update velocity
        deltaVelocity = acceleration.multiplyConstant(deltaTime);
        this.velocity = this.velocity.add(deltaVelocity);
        this.velocity = this.velocity.multiplyConstant(DAMPING);

        // Determine displacement
        displacement = this.velocity.multiplyConstant(deltaTime);
        
        // Find new x and y values     
        newX = this.innerNode.getX() + displacement.getX();
        newY = this.innerNode.getY() + displacement.getY();

        // Offset min and max to keep nodes fully in view
        minX += NODE_RADIUS;
        minY += NODE_RADIUS;
        maxX -= NODE_RADIUS;
        maxY -= NODE_RADIUS;

        // Make sure x and y are in range
        if(WALLS)
        {
            if(newX > maxX)
            {
                newX = maxX;
                this.velocity.setX(BOUNCE_CONSTANT * this.velocity.getX());
            }
            else if(newX < minX)
            {
                newX = minX;
                this.velocity.setX(BOUNCE_CONSTANT * this.velocity.getX());
            }
            
            if(newY > maxY)
            {
                newY = maxY;
                this.velocity.setY(BOUNCE_CONSTANT * this.velocity.getY());
            }
            else if(newY < minY)
            {
                newY = minY;
                this.velocity.setY(BOUNCE_CONSTANT * this.velocity.getY());
            }
        }

        // Set new x and y values
        this.innerNode.setX(newX);
        this.innerNode.setY(newY);

        return acceleration;
    }

    /**
     * Name: getID()
     * Desc: Determines the id of this node
     * Retr: The numerical id of this node
    **/
    this.getID = function()
    {
        return this.innerNode.getID();
    }
}

/**
 * Name: ForceEdgeDecorator(innerEdge)
 * Desc: Creates a new force edge around a given edge to
 *       temporarily provide mark sweep capabilities
 * Para: innerEdge, the edge this decorator should wrap
**/
function ForceEdgeDecorator(innerEdge)
{

    this.visited = false;
    this.innerEdge = innerEdge;

    // TODO: This is a bit messy and could be moved out of here now
    // It remains b/c the static length of the spring could be
    // taken into account later
    /**
     * Name: calcHooke(node)
     * Desc: Finds the "restoring" force of this edge if it is
     *       modeled as a spring
     * Para: targetNode, The node for which the force is being calculated
     *       otherNode, The other node on the other end of this edge
     * Retr: Force (instance) acting on the given node or null
     *       if error (b/c node was not on this edge)
    **/
    this.calcHooke = function(targetNode, otherNode)
    {
        var displacementX;
        var displacementY;
        var displacement;

        // Calculate magnitude
        displacementX = otherNode.getX() - targetNode.getX() + SPRING_OFFSET;
        displacementY = otherNode.getY() - targetNode.getY() + SPRING_OFFSET;
        magnitudeX = displacementX * SPRING_CONSTANT;
        magnitudeY = displacementY * SPRING_CONSTANT;

        return new Vector(magnitudeX, magnitudeY);
    }

    /**
     * Name: wasVisited()
     * Desc: Determines if this edge is marked as "visisted"
     * Retr: true if it was and false otherwise
    **/
    this.wasVisited = function()
    {
        return this.visited;
    }

    /**
     * Name: wasVisited()
     * Desc: Marks this edge as temporarily "visisted"
    **/
    this.markVisited = function()
    {
        this.visited = true;
    }

    /**
     * Name: reset()
     * Desc: Marks that this edge has not yet been visited
    **/
    this.reset = function()
    {
        this.visited = false;
    }

    /**
     * Name: getNodes()
     * Desc: Gets the two nodes on this edge
     * Retr: List of two elements, each a Node instance
    **/
    this.getNodes = function()
    {
        return this.innerEdge.getNodes();
    }
}
