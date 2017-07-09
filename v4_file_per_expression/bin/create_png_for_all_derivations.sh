# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# 20160129

rm -rf derivations/all
mkdir  derivations/all
find   derivations -depth 1 -type d | while read this_dir; do
    echo ${this_dir}
    # the newline is needed between files because some input files do not terminate with a new line
    cat "${this_dir}/derivation_edge_list.csv"       >> derivations/all/derivation_edge_list.csv
    printf "\n"                                      >> derivations/all/derivation_edge_list.csv
    cat "${this_dir}/expression_identifiers.csv"     >> derivations/all/expression_identifiers.csv
    printf "\n"                                      >> derivations/all/expression_identifiers.csv
    cat "${this_dir}/feeds.csv"                      >> derivations/all/feeds.csv
    printf "\n"                                      >> derivations/all/feeds.csv
    cat "${this_dir}/inference_rule_identifiers.csv" >> derivations/all/inference_rule_identifiers.csv
    printf "\n"                                      >> derivations/all/inference_rule_identifiers.csv
done
cat derivations/all/derivation_edge_list.csv       | sed '/^$/d' > derivations/all/derivation_edge_list.csv_temp
cat derivations/all/expression_identifiers.csv     | sed '/^$/d' > derivations/all/expression_identifiers.csv_temp
cat derivations/all/feeds.csv                      | sed '/^$/d' > derivations/all/feeds.csv_temp
cat derivations/all/inference_rule_identifiers.csv | sed '/^$/d' > derivations/all/inference_rule_identifiers.csv_temp

mv -f derivations/all/derivation_edge_list.csv_temp derivations/all/derivation_edge_list.csv
mv -f derivations/all/expression_identifiers.csv_temp derivations/all/expression_identifiers.csv
mv -f derivations/all/feeds.csv_temp derivations/all/feeds.csv
mv -f derivations/all/inference_rule_identifiers.csv_temp derivations/all/inference_rule_identifiers.csv

echo "calling bin/create_png_for_derivation__input_name_of_derivation.py derivations/all"
python bin/create_png_for_derivation__input_name_of_derivation.py "derivations/all"
