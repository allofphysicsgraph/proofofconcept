#!/bin/bash
# Ben Payne
# bash shell script to create deployable .tgz
todays_date=`date +%Y%m%d`
#svn_indx=`svn info | grep Revision | sed -ne 's/Revision: //p'`
git_indx=`git rev-parse HEAD`

folder_name=physics_graph_${todays_date}
mkdir ${folder_name}
#cp README.md                 ${folder_name}
#cp config.input              ${folder_name}

mkdir               ${folder_name}/derivations
cp -r ../derivations/* ${folder_name}/derivations

mkdir               ${folder_name}/identities
cp -r ../identities/*  ${folder_name}/identities

mkdir               ${folder_name}/expressions
cp ../expressions/*.tex ${folder_name}/expressions

mkdir               ${folder_name}/feeds
cp ../feeds/*.tex ${folder_name}/feeds

mkdir               ${folder_name}/inference_rules
cp ../inference_rules/* ${folder_name}/inference_rules

mkdir               ${folder_name}/templates
cp ../templates/* ${folder_name}/templates

mkdir               ${folder_name}/lib
cp ../../lib/*.py         ${folder_name}/lib/

mkdir               ${folder_name}/bin
cp *.py         ${folder_name}/bin/

# z=gzip, v=verbose, f=write to file
tar czvf physics_graph_v4_${todays_date}_git_${git_indx}.tgz ${folder_name}
echo "done making tgz"

rm -rf ${folder_name}

mv physics_graph_v4_${todays_date}_git_${git_indx}.tgz ../../

