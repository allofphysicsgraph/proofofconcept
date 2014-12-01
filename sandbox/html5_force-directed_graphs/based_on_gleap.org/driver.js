/**
 * Name: driver.js
 * Desc: Main driver for the node|art project
**/

var INFO_MESSAGE_DELAY = 3000;
var DESCRIPTION_BUTTON_DELAY = 4000;
var BUTTON_REAPPEAR_DELAY = 1000;
var ERROR_REAPPEAR_DELAY = 3000;

var CANVAS_WIDTH = 545;
var CANVAS_HEIGHT = 350;
var FRAME_DURATION = 20;
var MIN_ACCELERATION = 1;
var STARTING_NODES = 5;
var STARTING_CONNECTIONS= 5;
var MAX_NEW_NODE_EDGES = 3;
var MAX_NODES = 75;
var NODE_ADDITION_HEAT = 300;
var MAX_TEMP = 500;
var AUTO_OFFSET = 5;

var MAX_MESSAGE = "Sorry, you reached the maximum number of nodes.";

var previousTick;
var manager;
var canvas;
var context;
var errorDisplayed = false;

/**
 * Name: nodePlacementLoop(manager)
 * Para: manager, The GraphManager to operate on
 * Desc: Self-scheduling function that drives the force based
 *       graph visualization algorithm
**/
function nodePlacementLoop()
{
    // Find out how long it has been since we rendered
    var newTick = new Date();
    var deltaTime = newTick - previousTick;
    previousTick = newTick;

    // Update the configuration and cool system
    manager.updateGraphConfiguration(deltaTime / 7);

    // Clear and draw graph
    context.clearRect ( 0 , 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    manager.drawGraph(context);

    // Schedule to do it again
    setTimeout("nodePlacementLoop()", 2 * FRAME_DURATION - deltaTime); // FRAME_DURATION + (FRAME_DURATION - deltaTime)
}

/**
 * Name: addNode(e)
 * Desc: Adds a new node in response to user click
 * Para: e, Event information provided by jQuery
 * Note: Thanks http://stackoverflow.com/questions/3067691/html5-canvas-click-event
**/
function addNodeByClick(e)
{
    var i;
    var x = Math.floor((e.pageX-$("#nodeartCanvas").offset().left));
    var y = Math.floor((e.pageY-$("#nodeartCanvas").offset().top));
    var nextID = manager.getNextNodeID();
    var numNodes = manager.getNumNodes();
    var newNode;
    var newEdge;
    var id;
    var numEdges;
    var otherID;
    var otherNode;
    var currentNode;
    var newX;
    var newY;

    // If we reached the limit, finish
    if(numNodes == MAX_NODES)
    {
        if(errorDisplayed == false)
        {
            displayError(MAX_MESSAGE);
            errorDisplayed = true;

            setTimeout("errorDisplayed = false", ERROR_REAPPEAR_DELAY);
        }
        return;
    }

    // Make sure no one else is right on top
    for(i=0; i<numNodes; i++)
    {
        currentNode = manager.getNode(i);
        if(currentNode.getX() == x && currentNode.getY() == y)
        {
            i = 0; // Check from beginning again

            // Propose new x values
            newX = x - AUTO_OFFSET;
            newY = y - AUTO_OFFSET;

            // Correct if off screen
            if(newX < 0 || newX > CANVAS_WIDTH)
                newX = x + AUTO_OFFSET;
            if(newY < 0 || newY > CANVAS_HEIGHT)
                newY = y + AUTO_OFFSET;

            // Save new values
            x = newX;
            y = newY;
        }
    }

    // Create node
    newNode = new Node(x, y, nextID);
    manager.addNode(newNode);

    // Create edges
    numEdges = randInt(1, MAX_NEW_NODE_EDGES); // TODO: This is a bit messy
    for(i=0; i<numEdges; i++)
    {
        // Choose other node to link onto
        otherID = randInt(0, numNodes);
        otherNode = manager.getNode(otherID);

        // Add edge
        newEdge = new Edge(newNode, otherNode, true);
        manager.addEdge(newEdge);
    }
}

/**
 * Name: showInfo(event)
 * Desc: Event handler that shows the info div for this demo
 * Para: event, jQuery event information
**/
function showInfo(event)
{
    $("#nodeartCanvas").hide();
    $("#demoDescriptionButtonHolder").hide();
    $(".detailedDescription").slideDown();
    $("#lessInfoButtonHolder").delay(BUTTON_REAPPEAR_DELAY).fadeIn(); 
}

/**
 * Name: hideInfo(event)
 * Desc: Event handler that hides the info div for this demo
 * Para: event, jQuery event information
**/
function hideInfo(event)
{
    $(".detailedDescription").hide();
    $("#lessInfoButtonHolder").hide();
    $("#nodeartCanvas").slideDown();
    $("#demoDescriptionButtonHolder").delay(BUTTON_REAPPEAR_DELAY).fadeIn(); 
}

/**
 * Name: displayInfo()
 * Desc: Displays info about this demo
**/
function displayInfoWidgets()
{
    $("#demoInstructions").slideDown().delay(INFO_MESSAGE_DELAY).slideUp();
    $("#demoDescriptionButtonHolder").delay(DESCRIPTION_BUTTON_DELAY).fadeIn();
}

/**
 * Name: [document ready function]
 * Desc: Demo initalization called on page load
**/
$(document).ready(function() {

    // Hide information about the simulation
    $("#demoDescriptionButtonHolder").hide();
    $("#lessInfoButtonHolder").hide();
    $(".detailedDescription").hide();
    $("#demoInstructions").hide();

    // Get drawing context for canvas
    canvas = $("#nodeartCanvas")[0];
    canvas.setAttribute('width', CANVAS_WIDTH);
    canvas.setAttribute('height', CANVAS_HEIGHT);
    context = canvas.getContext("2d");

    // Setup click handers
    $("#nodeartCanvas").click(addNodeByClick);
    $("#moreInfoButton").click(showInfo);
    $("#lessInfoButton").click(hideInfo);
    
    // Create nodes and draw
    manager = new GraphManager(STARTING_NODES, STARTING_CONNECTIONS, 0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    // Display info soon
    setTimeout("displayInfoWidgets()", INFO_MESSAGE_DELAY);

    // Start mainloop for graph node placement
    previousTick = new Date();
    nodePlacementLoop(manager);
  
});