# Ben Payne <ben.is.located@gmail.com>
# Physics Derivation Graph
# 20160129

rm temp_id.dat
rm expr_id.dat
find ../derivations -depth 1 -type d | while read this_dir; do
    echo ${this_dir}
    cat "${this_dir}/derivation_edge_list.csv" | tr ',' '\n' >> temp_id.dat
    cat "${this_dir}/expression_identifiers.csv" | cut -d',' -f2 >> expr_id.dat
done
cat temp_id.dat | sort | uniq > temp_id2.dat
mv temp_id2.dat temp_id.dat
cat expr_id.dat | sort | uniq > expr_id2.dat
mv expr_id2.dat expr_id.dat

# at this point, we need to generate a new random index, then check that it doesn't already exist