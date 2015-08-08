# prints the commands for running each and all the derivations

cut -f 1 -d ',' databases/connections_database.csv | uniq > temp.dat

while read line; do 
  this_deriv=`echo $line | sed -e "s/ /_/g" | sed -e "s/\"//g"`
  file_name=output/${this_deriv}.html
  cp lib/d3js_part1_head.html ${file_name}
  echo -e "d3.json(\"http://allofphysicsgraph.github.io/proofofconcept/site/json/generated_from_project/"${this_deriv}".json\", function(error, root) {" >> ${file_name}
  cat lib/d3js_part2_tail.html >> ${file_name}
  
  echo -e "<P>Picture from Graphviz:</P>" >> ${file_name}
  echo -e "<P><img src=\"http://allofphysicsgraph.github.io/proofofconcept/site/pictures/generated_from_project/graph_"${this_deriv}"_without_labels.png\" width=\"800\"></P>" >> ${file_name}
  echo -e "</body>" >> ${file_name}
  echo -e "</html>" >> ${file_name}

  
done < temp.dat