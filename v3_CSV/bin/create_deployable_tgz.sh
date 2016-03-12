#!/bin/bash
# Ben Payne
# bash shell script to create deployable .tgz
todays_date=`date +%Y%m%d`
#svn_indx=`svn info | grep Revision | sed -ne 's/Revision: //p'`
git_indx=`git rev-parse HEAD`

folder_name=physics_graph_${todays_date}
mkdir ${folder_name}
cp README.md                 ${folder_name}
cp config.input              ${folder_name}
mkdir               ${folder_name}/output
mkdir               ${folder_name}/lib
cp lib/*.py         ${folder_name}/lib/
mkdir               ${folder_name}/lib/images_expression_png
mkdir               ${folder_name}/lib/images_feed_png
mkdir               ${folder_name}/lib/images_infrule_png   
mkdir               ${folder_name}/lib/images_expressions_svg
mkdir               ${folder_name}/lib/images_feed_svg
mkdir               ${folder_name}/lib/images_infrule_svg   
mkdir               ${folder_name}/bin
cp bin/*.py         ${folder_name}/bin/
mkdir               ${folder_name}/databases
cp databases/*.csv  ${folder_name}/databases
cp databases/README ${folder_name}/databases

# z=gzip, v=verbose, f=write to file
tar czvf physics_graph_${todays_date}_git_${git_indx}.tgz ${folder_name}

rm -rf ${folder_name}

echo "done making tgz"