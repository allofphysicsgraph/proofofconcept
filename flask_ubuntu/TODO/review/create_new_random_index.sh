#!/bin/sh

# Ben Payne <ben.is.located@gmail.com>
# Physics Derivation Graph
# 20160129

if [ -f temp_id.dat ] ; then
  rm temp_id.dat
fi
find derivations -depth 1 -type d | while read this_dir; do
    #echo "looking for temporary IDs in ${this_dir}"
    cat "${this_dir}/derivation_edge_list.csv" | tr ',' '\n' >> temp_id.dat # convert from two column to single column
done
find identities -depth 1 -type d | while read this_dir; do
    #echo "looking for temporary IDs in ${this_dir}"
    cat "${this_dir}/derivation_edge_list.csv" | tr ',' '\n' >> temp_id.dat # convert from two column to single column
done
# at this point we have a large single column list of temporary IDs
cat temp_id.dat | sort | uniq > temp_id2.dat
mv temp_id2.dat temp_id.dat


if [ -f expr_id.dat ]; then
  rm expr_id.dat
fi
find derivations -depth 1 -type d | while read this_dir; do
    #echo "looking for expression IDs in ${this_dir}"
    cat "${this_dir}/expression_identifiers.csv" | cut -d',' -f2 >> expr_id.dat # convert from two column to single column
done
find identities -depth 1 -type d | while read this_dir; do
    #echo "looking for expression IDs in ${this_dir}"
    cat "${this_dir}/expression_identifiers.csv" | cut -d',' -f2 >> expr_id.dat # convert from two column to single column
done
# at this point we have a large single column list of permanent IDs
cat expr_id.dat | sort | uniq > expr_id2.dat
mv expr_id2.dat expr_id.dat

# generate a new random index, then check that it doesn't already exist
# need a 10 digit random number
current_guess=`head -c10 <(echo $RANDOM$RANDOM$RANDOM$RANDOM$RANDOM)`
if grep -Fxq $current_guess expr_id.dat; then echo "already in file; try again"; else echo "perm ID not in use: $current_guess"; fi
