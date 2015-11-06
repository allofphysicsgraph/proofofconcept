#!/bin/bash
# prints the commands for running each and all the derivations

if [ "$#" -ne 2 ]; then
    echo -e "\nrequires 2 arguments:"
    echo -e "output path (ending in /)"
    echo -e "name of json file (no spaces, no extension)\n"
    exit
fi

# $1 = output path
# $2 = name of json file, no spaces, no extension

site_dir=testing
# site_dir=generated_from_project # actual PDG content

file_name=$1/$2.html
cp lib/d3js_part1_head.html ${file_name}
echo -e "d3.json(\"http://allofphysicsgraph.github.io/proofofconcept/site/json/"${site_dir}"/"$2".json\", function(error, root) {" >> ${file_name}
cat lib/d3js_part2_tail.html >> ${file_name}
  
echo -e "<P>Picture from Graphviz:</P>" >> ${file_name}
echo -e "<P><img src=\"http://allofphysicsgraph.github.io/proofofconcept/site/pictures/"${site_dir}"/graph_"$2"_without_labels.png\" width=\"800\"></P>" >> ${file_name}
echo -e "</body>" >> ${file_name}
echo -e "</html>" >> ${file_name}
  