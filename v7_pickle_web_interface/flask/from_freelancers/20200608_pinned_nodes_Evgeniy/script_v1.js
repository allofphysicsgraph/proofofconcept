// based on  https://bl.ocks.org/mapio/53fed7d84cd1812d6a6639ed7aa83868

// Collision Strength: 1.0 ~ 8.0
var collisionStrength = 1;

var width = 1000;
var height = 600;
var border = 1;
var bordercolor = "black";
var color = d3.scaleOrdinal(d3.schemeCategory10); // coloring of nodes

var graph = {
  "nodes": [
    {"id": "4747288", "group": 4, "img": "https://derivationmap.net/static/functionisodd.png", "url": "https://derivationmap.net/list_all_inference_rules?referrer=d3js#function is odd", "width": 207, "height": 25, "linear index": 4.4},
    {"id": "2394853829", "group": 0, "img": "https://derivationmap.net/static/2394853829.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#2394853829", "width": 451, "height": 34, "linear index": -1},
    {"id": "3848924", "group": 9, "img": "https://derivationmap.net/static/multiplybothsidesby.png", "url": "https://derivationmap.net/list_all_inference_rules?referrer=d3js#multiply both sides by", "width": 309, "height": 32, "linear index": 9},
    {"id": "3848927", "group": 2, "img": "https://derivationmap.net/static/changevariableXtoY.png", "url": "https://derivationmap.net/list_all_inference_rules?referrer=d3js#change variable X to Y", "width": 318, "height": 31, "linear index": 2.1},
    {"id": "3848592", "group": 5, "img": "https://derivationmap.net/static/addexpr1toexpr2.png", "url": "https://derivationmap.net/list_all_inference_rules?referrer=d3js#add expr 1 to expr 2", "width": 282, "height": 32, "linear index": 5},
    {"id": "0004829194", "group": 0, "img": "https://derivationmap.net/static/0004829194.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#0004829194", "width": 14, "height": 23, "linear index": -1},
    {"id": "0001030901", "group": 0, "img": "https://derivationmap.net/static/0001030901.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#0001030901", "width": 82, "height": 34, "linear index": -1},
    {"id": "4938429483", "group": 0, "img": "https://derivationmap.net/static/4938429483.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#4938429483", "width": 370, "height": 34, "linear index": -1},
    {"id": "2123139121", "group": 0, "img": "https://derivationmap.net/static/2123139121.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#2123139121", "width": 460, "height": 34, "linear index": -1},
    {"id": "4294921", "group": 12, "img": "https://derivationmap.net/static/swapLHSwithRHS.png", "url": "https://derivationmap.net/list_all_inference_rules?referrer=d3js#swap LHS with RHS", "width": 285, "height": 32, "linear index": 12},
    {"id": "0003981813", "group": 0, "img": "https://derivationmap.net/static/0003981813.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#0003981813", "width": 110, "height": 34, "linear index": -1},
    {"id": "0004849392", "group": 0, "img": "https://derivationmap.net/static/0004849392.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#0004849392", "width": 18, "height": 15, "linear index": -1},
    {"id": "4938429482", "group": 0, "img": "https://derivationmap.net/static/4938429482.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#4938429482", "width": 424, "height": 34, "linear index": -1},
    {"id": "7473895", "group": 1, "img": "https://derivationmap.net/static/declareinitialexpr.png", "url": "https://derivationmap.net/list_all_inference_rules?referrer=d3js#declare initial expr", "width": 257, "height": 32, "linear index": 1},
    {"id": "0003747849", "group": 0, "img": "https://derivationmap.net/static/0003747849.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#0003747849", "width": 39, "height": 23, "linear index": -1},
    {"id": "0001921933", "group": 0, "img": "https://derivationmap.net/static/0001921933.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#0001921933", "width": 25, "height": 23, "linear index": -1},
    {"id": "2384942", "group": 8, "img": "https://derivationmap.net/static/declarefinalexpr.png", "url": "https://derivationmap.net/list_all_inference_rules?referrer=d3js#declare final expr", "width": 236, "height": 32, "linear index": 8},
    {"id": "0003949052", "group": 0, "img": "https://derivationmap.net/static/0003949052.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#0003949052", "width": 43, "height": 15, "linear index": -1},
    {"id": "4843995999", "group": 0, "img": "https://derivationmap.net/static/4843995999.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#4843995999", "width": 453, "height": 46, "linear index": -1},
    {"id": "2849492", "group": 11, "img": "https://derivationmap.net/static/dividebothsidesby.png", "url": "https://derivationmap.net/list_all_inference_rules?referrer=d3js#divide both sides by", "width": 276, "height": 31, "linear index": 11},
    {"id": "9595949", "group": 3, "img": "https://derivationmap.net/static/functioniseven.png", "url": "https://derivationmap.net/list_all_inference_rules?referrer=d3js#function is even", "width": 216, "height": 25, "linear index": 3},
    {"id": "4938429484", "group": 0, "img": "https://derivationmap.net/static/4938429484.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#4938429484", "width": 399, "height": 34, "linear index": -1},
    {"id": "0003413423", "group": 0, "img": "https://derivationmap.net/static/0003413423.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#0003413423", "width": 109, "height": 34, "linear index": -1},
    {"id": "0002919191", "group": 0, "img": "https://derivationmap.net/static/0002919191.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#0002919191", "width": 107, "height": 34, "linear index": -1},
    {"id": "2949492", "group": 7, "img": "https://derivationmap.net/static/swapLHSwithRHS.png", "url": "https://derivationmap.net/list_all_inference_rules?referrer=d3js#swap LHS with RHS", "width": 285, "height": 32, "linear index": 7},
    {"id": "1928392", "group": 6, "img": "https://derivationmap.net/static/dividebothsidesby.png", "url": "https://derivationmap.net/list_all_inference_rules?referrer=d3js#divide both sides by", "width": 276, "height": 31, "linear index": 6},
    {"id": "3829492824", "group": 0, "img": "https://derivationmap.net/static/3829492824.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#3829492824", "width": 445, "height": 46, "linear index": -1},
    {"id": "3942849294", "group": 0, "img": "https://derivationmap.net/static/3942849294.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#3942849294", "width": 432, "height": 34, "linear index": -1},
    {"id": "0003919391", "group": 0, "img": "https://derivationmap.net/static/0003919391.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#0003919391", "width": 18, "height": 15, "linear index": -1},
    {"id": "4585932229", "group": 0, "img": "https://derivationmap.net/static/4585932229.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#4585932229", "width": 446, "height": 46, "linear index": -1},
    {"id": "2103023049", "group": 0, "img": "https://derivationmap.net/static/2103023049.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#2103023049", "width": 455, "height": 46, "linear index": -1},
    {"id": "0002393922", "group": 0, "img": "https://derivationmap.net/static/0002393922.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#0002393922", "width": 18, "height": 15, "linear index": -1},
    {"id": "4742644828", "group": 0, "img": "https://derivationmap.net/static/4742644828.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#4742644828", "width": 422, "height": 34, "linear index": -1},
    {"id": "2939404", "group": 10, "img": "https://derivationmap.net/static/addexpr1toexpr2.png", "url": "https://derivationmap.net/list_all_inference_rules?referrer=d3js#add expr 1 to expr 2", "width": 282, "height": 32, "linear index": 10}
  ],
  "links": [
    {"source": "2394853829", "target": "9595949", "value": 1},
    {"source": "0003981813", "target": "4747288", "value": 1},
    {"source": "3848927", "target": "2394853829", "value": 1},
    {"source": "4938429483", "target": "2939404", "value": 1},
    {"source": "0004849392", "target": "9595949", "value": 1},
    {"source": "0003919391", "target": "4747288", "value": 1},
    {"source": "4294921", "target": "2103023049", "value": 1},
    {"source": "0004829194", "target": "1928392", "value": 1},
    {"source": "4742644828", "target": "1928392", "value": 1},
    {"source": "4585932229", "target": "2384942", "value": 1},
    {"source": "0001921933", "target": "2849492", "value": 1},
    {"source": "2949492", "target": "4585932229", "value": 1},
    {"source": "4938429482", "target": "4747288", "value": 1},
    {"source": "4747288", "target": "4938429484", "value": 1},
    {"source": "4938429483", "target": "3848927", "value": 1},
    {"source": "2123139121", "target": "2939404", "value": 1},
    {"source": "4938429484", "target": "3848924", "value": 1},
    {"source": "0002919191", "target": "4747288", "value": 1},
    {"source": "2939404", "target": "3942849294", "value": 1},
    {"source": "4938429484", "target": "3848592", "value": 1},
    {"source": "2103023049", "target": "2384942", "value": 1},
    {"source": "3829492824", "target": "2949492", "value": 1},
    {"source": "3848592", "target": "4742644828", "value": 1},
    {"source": "0001030901", "target": "9595949", "value": 1},
    {"source": "0003949052", "target": "3848927", "value": 1},
    {"source": "3848924", "target": "2123139121", "value": 1},
    {"source": "0003413423", "target": "9595949", "value": 1},
    {"source": "0002393922", "target": "3848927", "value": 1},
    {"source": "4938429483", "target": "3848592", "value": 1},
    {"source": "1928392", "target": "3829492824", "value": 1},
    {"source": "0003747849", "target": "3848924", "value": 1},
    {"source": "7473895", "target": "4938429483", "value": 1},
    {"source": "9595949", "target": "4938429482", "value": 1},
    {"source": "2849492", "target": "4843995999", "value": 1},
    {"source": "4843995999", "target": "4294921", "value": 1},
    {"source": "3942849294", "target": "2849492", "value": 1}
  ]
};

var label = {
    "nodes": [],
    "links": []
};


graph.nodes.forEach(function (d, i) {
    label.nodes.push({ node: d });
    label.nodes.push({ node: d });
    label.links.push({
        source: i * 2,
        target: i * 2 + 1
    });
});

// COLLISION DETECT AND FIX
function rectCollide() {
    var nodes, sizes, masses
    var size = constant([0, 0])
    var strength = 1
    var iterations = 1

    function force() {
        var node, size, mass, xi, yi
        var i = -1
        while (++i < iterations) { iterate() }

        function iterate() {
            var j = -1
            var tree = d3.quadtree(nodes, xCenter, yCenter).visitAfter(prepare)

            while (++j < nodes.length) {
                node = nodes[j]
                size = sizes[j]
                mass = masses[j]
                xi = xCenter(node)
                yi = yCenter(node)

                tree.visit(apply)
            }
        }

        function apply(quad, x0, y0, x1, y1) {
            var data = quad.data
            var xSize = (size[0] + quad.size[0]) / 2
            var ySize = (size[1] + quad.size[1]) / 2
            if (data) {
                if (data.index <= node.index) { return }

                var x = xi - xCenter(data)
                var y = yi - yCenter(data)
                var xd = Math.abs(x) - xSize
                var yd = Math.abs(y) - ySize

                if (xd < 0 && yd < 0) {
                    var l = Math.sqrt(x * x + y * y)
                    var m = masses[data.index] / (mass + masses[data.index])

                    if (Math.abs(xd) < Math.abs(yd)) {
                        node.vx -= (x *= xd / l * strength) * m
                        data.vx += x * (1 - m)
                    } else {
                        node.vy -= (y *= yd / l * strength) * m
                        data.vy += y * (1 - m)
                    }
                }
            }

            return x0 > xi + xSize || y0 > yi + ySize ||
                x1 < xi - xSize || y1 < yi - ySize
        }

        function prepare(quad) {
            if (quad.data) {
                quad.size = sizes[quad.data.index]
            } else {
                quad.size = [0, 0]
                var i = -1
                while (++i < 4) {
                    if (quad[i] && quad[i].size) {
                        quad.size[0] = Math.max(quad.size[0], quad[i].size[0])
                        quad.size[1] = Math.max(quad.size[1], quad[i].size[1])
                    }
                }
            }
        }
    }

    function xCenter(d) { return d.x + d.vx + sizes[d.index][0] / 2 }
    function yCenter(d) { return d.y + d.vy + sizes[d.index][1] / 2 }

    force.initialize = function (_) {
        sizes = (nodes = _).map(size)
        masses = sizes.map(function (d) { return d[0] * d[1] })
    }

    force.size = function (_) {
        return (arguments.length
            ? (size = typeof _ === 'function' ? _ : constant(_), force)
            : size)
    }

    force.strength = function (_) {
        return (arguments.length ? (strength = +_, force) : strength)
    }

    force.iterations = function (_) {
        return (arguments.length ? (iterations = +_, force) : iterations)
    }

    return force
}

function constant(_) {
    return function () { return _ }
}


var collisionForce = rectCollide()
    .size(function (d) { return [d.width, d.height] })
    .strength(collisionStrength)

var labelLayout = d3.forceSimulation(label.nodes)
    .force("charge", d3.forceManyBody().strength(-50))
    .force("link", d3.forceLink(label.links).distance(0).strength(2));

var graphLayout = d3.forceSimulation(graph.nodes)
    .force("charge", d3.forceManyBody().strength(-3000))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("x", d3.forceX(width / 2).strength(1))
    .force("y", d3.forceY(height / 2).strength(1))
    .force("link", d3.forceLink(graph.links).id(function (d) { return d.id; }).distance(50).strength(1))
    .force('collision', collisionForce)
    .on("tick", ticked);

var adjlist = [];

graph.links.forEach(function (d) {
    adjlist[d.source.index + "-" + d.target.index] = true;
    adjlist[d.target.index + "-" + d.source.index] = true;
});

function neigh(a, b) {
    return a == b || adjlist[a + "-" + b];
}


var svg = d3.select("#viz").attr("width", width).attr("height", height);

// define arrow markers for graph links
svg.append("svg:defs").append("svg:marker")
    .attr("id", "end-arrow")
    .attr("viewBox", "0 -5 5 10") // min-x, min-y, width, height; https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/viewBox
    .attr("refX", 8) // x coordinate of an element's reference point; https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/refX
    .attr("markerWidth", 20) // width of the viewport; https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/markerWidth
    .attr("markerHeight", 20)
    .attr("orient", "auto")
    .append("svg:path")
    .attr("d", "M0,-3L6,0L0,3") // draw line starting at 0,-5; connect to 8,0, connect to 0,5
    .attr("fill", "gray");

// http://bl.ocks.org/AndrewStaroscik/5222370
var borderPath = svg.append("rect")
    .attr("x", 0)
    .attr("y", 0)
    .attr("height", height)
    .attr("width", width)
    .style("stroke", bordercolor)
    .style("fill", "none")
    .style("stroke-width", border);

var container = svg.append("g");

svg.call(
    d3.zoom()
        .scaleExtent([.1, 4])
        .on("zoom", function () { container.attr("transform", d3.event.transform); })
);

var link = container.append("g").attr("class", "links")
    .selectAll("line")
    .data(graph.links)
    .enter()
    .append("line")
    .attr("stroke", "#aaa")
    .attr("stroke-width", "2px")
    .attr("marker-end", "url(#end-arrow)");

var node = container.append("g").attr("class", "nodes")
    .selectAll("g")
    .data(graph.nodes)
    .enter()
    .append("a")
    .attr('href', function (d) { return d.url })
    .attr('target', '_blank')
    .append("circle")
    .attr("r", 10)
    .attr("fill", function (d) { return color(d.group); })

node.on("mouseover", focus).on("mouseout", unfocus);

node.call(
    d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended)
);

var labelNode = container.append("g").attr("class", "labelNodes")
    .selectAll("text")
    .data(label.nodes)
    .enter() // https://www.d3indepth.com/enterexit/
    // the following three lines hyperlink the image
    .append("a")
    .attr('href', function (d, i) { return d.node.url })
    .attr('target', '_blank')
    .append("image")
    // alternative option, unverified: https://stackoverflow.com/questions/39908583/d3-js-labeling-nodes-with-image-in-force-layout
    // BHP does not know why the i%2 is needed; without it the graph gets two images per node
    // see "label.links.push" above which uses this even/odd identifier
    // switching between i%2==1 and i%2==0 produces different image locations (?)
    .attr("xlink:href", function (d, i) { return i % 2 == 1 ? "" : d.node.img; })
    .attr("x", 4)
    .attr("y", 0)
    // the following alter the image size
    .attr("width", function (d, i) { return d.node.width / 2; })
    .attr("height", function (d, i) { return d.node.height / 2; });

node.on("mouseover", focus).on("mouseout", unfocus);

// get nodes, images and links for top and bottom linear indices
var minLinear = Infinity, maxLinear = 0;

graph.nodes.forEach(function(d) {
    if (d['linear index'] > 0) {
        if (d['linear index'] < minLinear) {
            minLinear = d['linear index'];
        }
        
        if (d['linear index'] > maxLinear) {
            maxLinear = d['linear index'];
        }
    }
});

var topNode = d3.selectAll('.nodes circle')
    .filter(function(d) {
        return d['linear index'] > 0 && d['linear index'] == minLinear;
    });

var bottNode = d3.selectAll('.nodes circle')
    .filter(function(d) {
        return d['linear index'] > 0 && d['linear index'] == maxLinear;
    });

var topId = topNode.data()[0].id;
var bottId = bottNode.data()[0].id;

var topLabel = d3.selectAll('.labelNodes image')
    .filter(function(d) {
        return d.node.id == topId;
    });

var bottLabel = d3.selectAll('.labelNodes image')
    .filter(function(d) {
        return d.node.id == bottId;
    });

var topSourceLink = d3.selectAll('.links line')
    .filter(function(d) {
        return d.source.id == topId;
    });

var topTargetLink = d3.selectAll('.links line')
    .filter(function(d) {
        return d.target.id == topId;
    });

var bottSourceLink = d3.selectAll('.links line')
    .filter(function(d) {
        return d.source.id == bottId;
    });

var bottTargetLink = d3.selectAll('.links line')
    .filter(function(d) {
        return d.target.id == bottId;
    });

var minY = Infinity, maxY = -Infinity;

function ticked() {
    minY = Infinity;
    maxY = -Infinity;

    node.call(updateNode);
    link.call(updateLink);

    // repositioning top and bottom nodes and links: start
    topNode.fixed = true;
    topNode.attr('transform', function(d) {
        return 'translate(' + fixna(d.x) + ',' + (minY - 30) + ')'
    });
    bottNode.fixed = true;
    bottNode.attr('transform', function(d) {
        return 'translate(' + fixna(d.x) + ',' + (maxY + 30) + ')'
    });

    topSourceLink.attr("y1", function (d) { 
        return (minY - 30); 
    });

    topTargetLink.attr("y2", function (d) { 
        return (minY - 30); 
    });

    bottSourceLink.attr("y1", function (d) { 
        return (maxY + 30); 
    });

    bottTargetLink.attr("y2", function (d) { 
        return (maxY + 30); 
    });
    // repositioning top and bottom nodes and links: end

    labelLayout.alphaTarget(0.3).restart();
    labelNode.each(function (d, i) {
        if (i % 2 == 0) {
            d.x = d.node.x;
            d.y = d.node.y;
        } else {
            var b = this.getBBox();

            var diffX = d.x - d.node.x;
            var diffY = d.y - d.node.y;

            var dist = Math.sqrt(diffX * diffX + diffY * diffY);

            var shiftX = b.width * (diffX - dist) / (dist * 2);
            shiftX = Math.max(-b.width, Math.min(0, shiftX));
            var shiftY = 16;
            this.setAttribute("transform", "translate(" + shiftX + "," + shiftY + ")");
        }
    });
    labelNode.call(updateNode);

    // repositioning top and bottom labels: start
    topLabel.each(function(d) {
        d.fixed = true;

        if (this.getAttribute('transform')) {
            var tx = +this.getAttribute('transform').split(/[(),]/)[1];
            var ty = +this.getAttribute('transform').split(/[(),]/)[2];
            this.setAttribute("transform", "translate(" + tx + "," + (ty - d.node.y + minY - 10) + ")");
        }
    });
    bottLabel.each(function(d) {
        d.fixed = true;

        if (this.getAttribute('transform')) {
            var tx = +this.getAttribute('transform').split(/[(),]/)[1];
            var ty = +this.getAttribute('transform').split(/[(),]/)[2];
            this.setAttribute("transform", "translate(" + tx + "," + (ty - d.node.y + maxY + 16) + ")");
        }
    });
    // repositioning top and bottom labels: start
}

function fixna(x) {
    if (isFinite(x)) return x;
    return 0;
}

function focus(d) {
    var index = d3.select(d3.event.target).datum().index;
    node.style("opacity", function (o) {
        return neigh(index, o.index) ? 1 : 0.1;
    });
    labelNode.attr("display", function (o) {
        return neigh(index, o.node.index) ? "block" : "none";
    });
    link.style("opacity", function (o) {
        return o.source.index == index || o.target.index == index ? 1 : 0.1;
    });
}

function unfocus() {
    labelNode.attr("display", "block");
    node.style("opacity", 1);
    link.style("opacity", 1);
}

function updateLink(link) {
    link.attr("x1", function (d) { return fixna(d.source.x); })
        .attr("y1", function (d) { return fixna(d.source.y); })
        .attr("x2", function (d) { return fixna(d.target.x); })
        .attr("y2", function (d) { return fixna(d.target.y); });
}

function updateNode(node) {
    node.attr("transform", function (d) {
        if (fixna(d.y) < minY) {
            minY = fixna(d.y);
        }

        if (fixna(d.y) > maxY) {
            maxY = fixna(d.y);
        }

        return "translate(" + fixna(d.x) + "," + fixna(d.y) + ")";
    });
}

function dragstarted(d) {
    d3.event.sourceEvent.stopPropagation();
    if (!d3.event.active) graphLayout.alphaTarget(0.1).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

function dragended(d) {
    if (!d3.event.active) graphLayout.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}
