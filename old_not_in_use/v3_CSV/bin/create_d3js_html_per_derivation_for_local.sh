#!/bin/bash
# prints the commands for running each and all the derivations

if [ "$#" -ne 5 ]; then
    echo -e "\nrequires 5 arguments:"
    echo -e "path to output html file (ending in /)\n"             # $1
    echo -e "path to output json file (ending in /)\n"             # $2
    echo -e "path to picture          (ending in /)\n"             # $3
    echo -e "name of derivation file  (no spaces, no extension)\n" # $4
    echo -e "local or web\n"                                       # $5
    exit
fi

file_name=$1$4.html
cp lib/d3js_part1_head_for_$5.html ${file_name}
echo -e "d3.json(\""$2$4".json\", function(error, root) {" >> ${file_name}
cat lib/d3js_part2_tail.html >> ${file_name}
  
echo -e "<P>Picture from Graphviz:</P>" >> ${file_name}
echo -e "<P><img src=\""$3$4"_without_labels.png\" width=\"800\"></P>" >> ${file_name}
echo -e "</body>" >> ${file_name}
echo -e "</html>" >> ${file_name}
  