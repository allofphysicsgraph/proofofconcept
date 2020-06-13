// based on  https://bl.ocks.org/mapio/53fed7d84cd1812d6a6639ed7aa83868

var width = 600;
var height = 400;
var border = 1;
var bordercolor="black";
var color = d3.scaleOrdinal(d3.schemeCategory10); // coloring of nodes

var graph = {
  "nodes": [
{"id": "000002", "group": 0, "img": "https://derivationmap.net/static/000002_name.png", "url": "https://derivationmap.net/review_derivation/000002/?referrer=d3js", "width": 439, "height": 32, "linear index": 0},
{"id": "000003", "group": 0, "img": "https://derivationmap.net/static/000003_name.png", "url": "https://derivationmap.net/review_derivation/000003/?referrer=d3js", "width": 538, "height": 32, "linear index": 0},
{"id": "000004", "group": 0, "img": "https://derivationmap.net/static/000004_name.png", "url": "https://derivationmap.net/review_derivation/000004/?referrer=d3js", "width": 676, "height": 32, "linear index": 0},
{"id": "9988949211", "group": 1, "img": "https://derivationmap.net/static/9988949211.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#9988949211", "width": 284, "height": 53, "linear index": 0},
{"id": "551770", "group": 0, "img": "https://derivationmap.net/static/551770_name.png", "url": "https://derivationmap.net/review_derivation/551770/?referrer=d3js", "width": 318, "height": 25, "linear index": 0},
{"id": "000011", "group": 0, "img": "https://derivationmap.net/static/000011_name.png", "url": "https://derivationmap.net/review_derivation/000011/?referrer=d3js", "width": 406, "height": 32, "linear index": 0},
{"id": "000015", "group": 0, "img": "https://derivationmap.net/static/000015_name.png", "url": "https://derivationmap.net/review_derivation/000015/?referrer=d3js", "width": 471, "height": 32, "linear index": 0},
{"id": "2103023049", "group": 1, "img": "https://derivationmap.net/static/2103023049.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#2103023049", "width": 455, "height": 46, "linear index": 0},
{"id": "3131111133", "group": 1, "img": "https://derivationmap.net/static/3131111133.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#3131111133", "width": 121, "height": 34, "linear index": 0},
{"id": "3121513111", "group": 1, "img": "https://derivationmap.net/static/3121513111.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#3121513111", "width": 95, "height": 47, "linear index": 0},
{"id": "539398", "group": 0, "img": "https://derivationmap.net/static/539398_name.png", "url": "https://derivationmap.net/review_derivation/539398/?referrer=d3js", "width": 661, "height": 34, "linear index": 0},
{"id": "000005", "group": 0, "img": "https://derivationmap.net/static/000005_name.png", "url": "https://derivationmap.net/review_derivation/000005/?referrer=d3js", "width": 231, "height": 31, "linear index": 0},
{"id": "387954", "group": 0, "img": "https://derivationmap.net/static/387954_name.png", "url": "https://derivationmap.net/review_derivation/387954/?referrer=d3js", "width": 373, "height": 32, "linear index": 0},
{"id": "000008", "group": 0, "img": "https://derivationmap.net/static/000008_name.png", "url": "https://derivationmap.net/review_derivation/000008/?referrer=d3js", "width": 261, "height": 32, "linear index": 0},
{"id": "7575859295", "group": 1, "img": "https://derivationmap.net/static/7575859295.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#7575859295", "width": 455, "height": 42, "linear index": 0},
{"id": "000006", "group": 0, "img": "https://derivationmap.net/static/000006_name.png", "url": "https://derivationmap.net/review_derivation/000006/?referrer=d3js", "width": 482, "height": 32, "linear index": 0},
{"id": "187793", "group": 0, "img": "https://derivationmap.net/static/187793_name.png", "url": "https://derivationmap.net/review_derivation/187793/?referrer=d3js", "width": 502, "height": 34, "linear index": 0},
{"id": "918264", "group": 0, "img": "https://derivationmap.net/static/918264_name.png", "url": "https://derivationmap.net/review_derivation/918264/?referrer=d3js", "width": 458, "height": 32, "linear index": 0},
{"id": "8494839423", "group": 1, "img": "https://derivationmap.net/static/8494839423.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#8494839423", "width": 227, "height": 60, "linear index": 0},
{"id": "000017", "group": 0, "img": "https://derivationmap.net/static/000017_name.png", "url": "https://derivationmap.net/review_derivation/000017/?referrer=d3js", "width": 456, "height": 34, "linear index": 0},
{"id": "884319", "group": 0, "img": "https://derivationmap.net/static/884319_name.png", "url": "https://derivationmap.net/review_derivation/884319/?referrer=d3js", "width": 291, "height": 32, "linear index": 0},
{"id": "2113211456", "group": 1, "img": "https://derivationmap.net/static/2113211456.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#2113211456", "width": 121, "height": 34, "linear index": 0},
{"id": "000010", "group": 0, "img": "https://derivationmap.net/static/000010_name.png", "url": "https://derivationmap.net/review_derivation/000010/?referrer=d3js", "width": 276, "height": 32, "linear index": 0},
{"id": "9882526611", "group": 1, "img": "https://derivationmap.net/static/9882526611.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#9882526611", "width": 204, "height": 35, "linear index": 0},
{"id": "1405465835", "group": 1, "img": "https://derivationmap.net/static/1405465835.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#1405465835", "width": 323, "height": 46, "linear index": 0},
{"id": "4938429483", "group": 1, "img": "https://derivationmap.net/static/4938429483.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#4938429483", "width": 370, "height": 34, "linear index": 0},
{"id": "2405307372", "group": 1, "img": "https://derivationmap.net/static/2405307372.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#2405307372", "width": 335, "height": 34, "linear index": 0},
{"id": "201726", "group": 0, "img": "https://derivationmap.net/static/201726_name.png", "url": "https://derivationmap.net/review_derivation/201726/?referrer=d3js", "width": 671, "height": 32, "linear index": 0},
{"id": "3131211131", "group": 1, "img": "https://derivationmap.net/static/3131211131.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#3131211131", "width": 122, "height": 30, "linear index": 0},
{"id": "5438722682", "group": 1, "img": "https://derivationmap.net/static/5438722682.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#5438722682", "width": 267, "height": 34, "linear index": 0},
{"id": "000009", "group": 0, "img": "https://derivationmap.net/static/000009_name.png", "url": "https://derivationmap.net/review_derivation/000009/?referrer=d3js", "width": 273, "height": 32, "linear index": 0},
{"id": "522862", "group": 0, "img": "https://derivationmap.net/static/522862_name.png", "url": "https://derivationmap.net/review_derivation/522862/?referrer=d3js", "width": 614, "height": 32, "linear index": 0},
{"id": "000016", "group": 0, "img": "https://derivationmap.net/static/000016_name.png", "url": "https://derivationmap.net/review_derivation/000016/?referrer=d3js", "width": 783, "height": 34, "linear index": 0},
{"id": "000013", "group": 0, "img": "https://derivationmap.net/static/000013_name.png", "url": "https://derivationmap.net/review_derivation/000013/?referrer=d3js", "width": 408, "height": 32, "linear index": 0},
{"id": "4585932229", "group": 1, "img": "https://derivationmap.net/static/4585932229.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#4585932229", "width": 446, "height": 46, "linear index": 0},
{"id": "000012", "group": 0, "img": "https://derivationmap.net/static/000012_name.png", "url": "https://derivationmap.net/review_derivation/000012/?referrer=d3js", "width": 891, "height": 32, "linear index": 0},
{"id": "9862900242", "group": 1, "img": "https://derivationmap.net/static/9862900242.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#9862900242", "width": 385, "height": 46, "linear index": 0},
{"id": "000018", "group": 0, "img": "https://derivationmap.net/static/000018_name.png", "url": "https://derivationmap.net/review_derivation/000018/?referrer=d3js", "width": 509, "height": 31, "linear index": 0},
{"id": "2131616531", "group": 1, "img": "https://derivationmap.net/static/2131616531.png", "url": "https://derivationmap.net/list_all_expressions?referrer=d3js#2131616531", "width": 103, "height": 30, "linear index": 0},
{"id": "332170", "group": 0, "img": "https://derivationmap.net/static/332170_name.png", "url": "https://derivationmap.net/review_derivation/332170/?referrer=d3js", "width": 1003, "height": 34, "linear index": 0},
{"id": "000001", "group": 0, "img": "https://derivationmap.net/static/000001_name.png", "url": "https://derivationmap.net/review_derivation/000001/?referrer=d3js", "width": 286, "height": 32, "linear index": 0},
{"id": "000007", "group": 0, "img": "https://derivationmap.net/static/000007_name.png", "url": "https://derivationmap.net/review_derivation/000007/?referrer=d3js", "width": 970, "height": 32, "linear index": 0},
{"id": "000014", "group": 0, "img": "https://derivationmap.net/static/000014_name.png", "url": "https://derivationmap.net/review_derivation/000014/?referrer=d3js", "width": 229, "height": 25, "linear index": 0}
  ],
  "links": [
    {"source": "918264", "target": "9882526611", "value": 1},
    {"source": "884319", "target": "2113211456", "value": 1},
    {"source": "000008", "target": "3131111133", "value": 1},
    {"source": "000008", "target": "3121513111", "value": 1},
    {"source": "000005", "target": "7575859295", "value": 1},
    {"source": "000003", "target": "2103023049", "value": 1},
    {"source": "201726", "target": "2405307372", "value": 1},
    {"source": "000001", "target": "4938429483", "value": 1},
    {"source": "000016", "target": "2103023049", "value": 1},
    {"source": "000004", "target": "8494839423", "value": 1},
    {"source": "000006", "target": "3121513111", "value": 1},
    {"source": "187793", "target": "1405465835", "value": 1},
    {"source": "201726", "target": "5438722682", "value": 1},
    {"source": "000016", "target": "2405307372", "value": 1},
    {"source": "000003", "target": "4938429483", "value": 1},
    {"source": "000006", "target": "3131211131", "value": 1},
    {"source": "000003", "target": "4585932229", "value": 1},
    {"source": "884319", "target": "3131111133", "value": 1},
    {"source": "000002", "target": "9988949211", "value": 1},
    {"source": "187793", "target": "9882526611", "value": 1},
    {"source": "000010", "target": "9988949211", "value": 1},
    {"source": "187793", "target": "5438722682", "value": 1},
    {"source": "000008", "target": "2131616531", "value": 1},
    {"source": "187793", "target": "9862900242", "value": 1},
    {"source": "918264", "target": "1405465835", "value": 1},
    {"source": "201726", "target": "9862900242", "value": 1},
    {"source": "000007", "target": "8494839423", "value": 1},
    {"source": "884319", "target": "2131616531", "value": 1},
    {"source": "000008", "target": "3131211131", "value": 1},
    {"source": "539398", "target": "4585932229", "value": 1},
    {"source": "000016", "target": "4585932229", "value": 1},
    {"source": "000017", "target": "4938429483", "value": 1},
    {"source": "000002", "target": "4938429483", "value": 1},
    {"source": "000004", "target": "7575859295", "value": 1},
    {"source": "000008", "target": "2113211456", "value": 1}
  ]
};

var label = {
    "nodes": [],
    "links": []
};

graph.nodes.forEach(function(d, i) {
    label.nodes.push({node: d});
    label.nodes.push({node: d});
    label.links.push({
        source: i * 2,
        target: i * 2 + 1
    });
});

var labelLayout = d3.forceSimulation(label.nodes)
    .force("charge", d3.forceManyBody().strength(-50))
    .force("link", d3.forceLink(label.links).distance(0).strength(2));

var graphLayout = d3.forceSimulation(graph.nodes)
    .force("charge", d3.forceManyBody().strength(-3000))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("x", d3.forceX(width / 2).strength(1))
    .force("y", d3.forceY(height / 2).strength(1))
    .force("link", d3.forceLink(graph.links).id(function(d) {return d.id; }).distance(50).strength(1))
    .on("tick", ticked);

var adjlist = [];

graph.links.forEach(function(d) {
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
        .on("zoom", function() { container.attr("transform", d3.event.transform); })
);

var link = container.append("g").attr("class", "links")
    .selectAll("line")
    .data(graph.links)
    .enter()
    .append("line")
    .attr("stroke", "#aaa")
    .attr("stroke-width", "2px")
    .attr("marker-end","url(#end-arrow)");

var node = container.append("g").attr("class", "nodes")
    .selectAll("g")
    .data(graph.nodes)
    .enter()
    .append("a")
    .attr('href', function(d) { return d.url })
    .attr('target', '_blank')
    .append("circle")
    .attr("r", 10)
    .attr("fill", function(d) { return color(d.group); })

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
    .attr('href', function(d, i) { return d.node.url })
    .attr('target', '_blank')
    .append("image")
    // alternative option, unverified: https://stackoverflow.com/questions/39908583/d3-js-labeling-nodes-with-image-in-force-layout
    // BHP does not know why the i%2 is needed; without it the graph gets two images per node
    // see "label.links.push" above which uses this even/odd identifier
    // switching between i%2==1 and i%2==0 produces different image locations (?)
    .attr("xlink:href", function(d, i) { return i % 2 == 1 ? "" : d.node.img; } )
    .attr("x", 4)
    .attr("y", 0)
    // the following alter the image size
    .attr("width", function(d, i) { return d.node.width/2; })
    .attr("height", function(d, i) { return d.node.height/2; });

node.on("mouseover", focus).on("mouseout", unfocus);

function ticked() {

    node.call(updateNode);
    link.call(updateLink);

    labelLayout.alphaTarget(0.3).restart();
    labelNode.each(function(d, i) {
        if(i % 2 == 0) {
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

}

function fixna(x) {
    if (isFinite(x)) return x;
    return 0;
}

function focus(d) {
    var index = d3.select(d3.event.target).datum().index;
    node.style("opacity", function(o) {
        return neigh(index, o.index) ? 1 : 0.1;
    });
    labelNode.attr("display", function(o) {
      return neigh(index, o.node.index) ? "block": "none";
    });
    link.style("opacity", function(o) {
        return o.source.index == index || o.target.index == index ? 1 : 0.1;
    });
}

function unfocus() {
   labelNode.attr("display", "block");
   node.style("opacity", 1);
   link.style("opacity", 1);
}

function updateLink(link) {
    link.attr("x1", function(d) { return fixna(d.source.x); })
        .attr("y1", function(d) { return fixna(d.source.y); })
        .attr("x2", function(d) { return fixna(d.target.x); })
        .attr("y2", function(d) { return fixna(d.target.y); });
}

function updateNode(node) {
    node.attr("transform", function(d) {
        return "translate(" + fixna(d.x) + "," + fixna(d.y) + ")";
    });
}

function dragstarted(d) {
    d3.event.sourceEvent.stopPropagation();
    if (!d3.event.active) graphLayout.alphaTarget(0.3).restart();
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
