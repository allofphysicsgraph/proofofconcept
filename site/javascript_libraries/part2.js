  force
      .nodes(root.nodes)
      .links(root.links)
      .start();

  var link = vis.selectAll(".link")
        .data(root.links)
        .enter().append("line")
          .attr("class", "link")
          .attr("stroke", "#666") // #CCC is a light gray 
          .attr("fill", "none")
          .attr("marker-end", "url(#end)");
    
  var node = vis.selectAll("circle.node")
      .data(root.nodes)
      .enter().append("g")
      .attr("class", "node")
      .call(force.drag);

  node.append("svg:circle")
//      .attr("cx", function(d) { return d.x; })
//      .attr("cy", function(d) { return d.y; })
      .attr("r", circleWidth)
      .attr("fill", palette.darkgray )

  node.append("text")
      .text(function(d, i) { return d.label; })
      .attr("x",  5) // positive value moves text right of origin
      .attr("y",  -3) // positive value moves text up from origin
      .attr("font-family",  "Bree Serif")
      .attr("fill",    palette.red)
      .attr("font-size",    "1em" )
      //.attr("text-anchor",  function(d, i) { if (i>0) { return  "beginning"; }      else { return "end" } })

  node.append("image")
      .attr("xlink:href", function(d, i) { return d.img; } )
      // setting x and y both to zero is redundant -- those are the default values
      .attr("x", 0) // off-set from center of node; upper left corner of picture is origin
      .attr("y", 0)
      .attr("width", function(d, i) { return d.width/2; }) // without both width and height, image does not display
//      .attr("width", 200) // without both width and height, image does not display
      .attr("height", function(d, i) { return d.height/2; })

  force.on("tick", function(e) {
    node.attr("transform", function(d, i) {     
      return "translate(" + d.x + "," + d.y + ")"; 
    });
    
    link.attr("x1", function(d)   { return d.source.x; })
        .attr("y1", function(d)   { return d.source.y; })
        .attr("x2", function(d)   { return d.target.x; })
        .attr("y2", function(d)   { return d.target.y; })
  }); // force.on

  force.start();

});
