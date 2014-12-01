/**
 * Name: vector.js
 * Desc: Simple structure to contain information about vectors
 *       and do simple calculations
**/

/**
 * Name: buildComponentVector(magnitude, direction)
 * Desc: Creates a new Vector instance from the given magnitude and
 *       direction
 * Para: magnitude, The length of this vector
 *       direction, Rad between the direction of this vector and 
 *                  due right
**/
function buildComponentVector(magnitude, direction)
{
	var xComponent = magnitude * Math.cos(direction);
	var yComponent = magnitude * Math.sin(direction);

	return new Vector(xComponent, yComponent);
}

/**
 * Name: Vector(xComponent, yComponent)
 * Desc: Creates a new vector with the given components
 * Para: xComponent, the x component of this vector
 *       yComponent, the y component of this vector
**/
function Vector(xComponent, yComponent)
{
	this.xComponent = xComponent;
	this.yComponent = yComponent;

	/**
	 * Name: generateOpposing()
	 * Desc: Creates a new vector that is the exact opposite
	 *       of this vector (pointing the opposite direction)
	 * Retr: New Vector instance
	**/
	this.generateOpposing = function()
	{
		return new Vector(-this.xComponent, -this.yComponent);	
	}

	/**
	 * Name: getX()
	 * Desc: Gets the x component of this vector
	 * Retr: The x component of this vector
	**/
	this.getX = function()
	{
		return this.xComponent;
	}

	/**
	 * Name: getY()
	 * Desc: Gets the y component of this vector
	 * Retr: The y component of this vector
	**/
	this.getY = function()
	{
		return this.yComponent;
	}

	/**
	 * Name: setX(newX)
	 * Desc: Sets this vector's x component
	 * Para: newX, this vector's new x component
	**/
	this.setX = function(newX)
	{
		this.xComponent = newX;
	}

	/**
	 * Name: setY(newY)
	 * Desc: Sets this vector's y component
	 * Para: newY, this vector's new y component
	**/
	this.setY = function(newY)
	{
		this.yComponent = newY;
	}

	/**
	 * Name: add(other)
	 * Desc: Adds this vector to other and returns a new vector
	 *		 with the result
	 * Para: other, The vector that this vector is to be added to
	 * Retr: New vector that equals this vector plus other
	**/
	this.add = function(other)
	{
		var newX = this.getX() + other.getX();
		var newY = this.getY() + other.getY();
		return new Vector(newX, newY);
	}

	/**
	 * Name: sub(other)
	 * Desc: Subtracts the other vector from this oneand returns a 
	 *		 new vector with the result
	 * Para: other, The vector to subtract from this one
	 * Retr: New vector that equals this vector minus the other
	**/
	this.sub = function(other)
	{
		var newX = this.getX() - other.getX();
		var newY = this.getY() - other.getY();
		return new Vector(newX, newY);
	}

	/**
	 * Name: dot(other)
	 * Desc: Finds the dot product between this vector and other
	 * Para: Other, the other vector to find the dot product with
	 * Retr: Dot product between this and other
	**/
	this.dot = function(other)
	{
		var x = this.getX() * other.getX();
		var y = this.getY() * other.getY();
		return x + y;
	}

	/**
	 * Name: mulitplyConstant(constant)
	 * Desc: Multiplies this entire vector by a scalar constant
	 * Para: constant, The constant to multiply this vector by
	 * Retr: This vector after multiplication
	**/
	this.multiplyConstant = function(constant)
	{
		var newX = this.getX() * constant;
		var newY = this.getY() * constant;

		return new Vector(newX, newY);
	}

	/**
	 * Name: getMagnitude()
	 * Desc: Determines the norm or magnitude of this vector
	 * Retr: The length of this vector
	**/
	this.getMagnitude = function()
	{
		return Math.sqrt(Math.pow(this.getX(), 2) + Math.pow(this.getY(), 2));
	}
}