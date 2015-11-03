#!/bin/bash
# Ben Payne
# bash shell script to create deployable .tgz
todays_date=`date +%Y%m%d`
#svn_indx=`svn info | grep Revision | sed -ne 's/Revision: //p'`
git_indx=`git rev-parse HEAD`

folder_name=physics_graph_${todays_date}
mkdir ${folder_name}
cp README                   ${folder_name}
cp create_deployable_tgz.sh ${folder_name}
cp run_each_too.sh          ${folder_name}
cp config.input             ${folder_name}
mkdir ${folder_name}/output

mkdir       ${folder_name}/lib
cp lib/*.py ${folder_name}/lib/
mkdir       ${folder_name}/lib/images_eq_png
mkdir       ${folder_name}/lib/images_feed_png
mkdir       ${folder_name}/lib/images_op_png   
mkdir       ${folder_name}/lib/images_eq_svg
mkdir       ${folder_name}/lib/images_feed_svg
mkdir       ${folder_name}/lib/images_op_svg   

mkdir       ${folder_name}/bin
cp bin/*.py ${folder_name}/bin/

mkdir              ${folder_name}/databases
cp databases/*.xml ${folder_name}/databases

tar czvf physics_graph_${todays_date}_svn${git_indx}.tgz ${folder_name}

rm -rf ${folder_name}

echo "done making tgz"