/**
 * Name: util.js
 * Desc: Common utility routines for Gleap.org
**/

var MESSAGE_DURATION = 3000;

var displayingError = false;

/**
 * Name: randInt(min, max)
 * Desc: Generates a random number in [min, max)
 *       or between min and max-1
 * Para: min, The minimum allowed number to generate
 *       max, The maximum allowed number to generate
**/
function randInt(min, max)
{
    var range = max - min;
    return Math.floor(Math.random()*range) + min;
}

// Array Remove - By John Resig (MIT Licensed)
Array.prototype.remove = function(from, to) {
    var rest = this.slice((to || from) + 1 || this.length);
    this.length = from < 0 ? this.length + from : from;
    return this.push.apply(this, rest);
};

Array.prototype.empty = function()
{
    return this.length == 0;
}

/**
 * Name: displayError(message)
 * Desc: Displays an error message to the user
 * Para: message, The message to display
**/
function displayError(message)
{
    $("#errorDisplay").hide();
    $("#errorDisplay").html(message);
    $("#errorDisplay").slideDown().delay(MESSAGE_DURATION).slideUp();
}

/**
 * Name: displayInfo(message)
 * Desc: Displays an info message to the user
 * Para: message, The message to display
**/
function displayInfo(message)
{
    $("#infoDisplay").hide();
    $("#infoDisplay").html(message);
    $("#infoDisplay").slideDown().delay(MESSAGE_DURATION).slideUp();
}