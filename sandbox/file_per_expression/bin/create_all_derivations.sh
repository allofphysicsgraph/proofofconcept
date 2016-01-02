rm -rf ../derivations/all
mkdir ../derivations/all
find ../derivations -depth 1 -type d | while read this_dir; do
    echo ${this_dir}
    cat "${this_dir}/derivation_edge_list.csv" >> ../derivations/all/derivation_edge_list.csv
    cat "${this_dir}/expression_identifiers.csv" >> ../derivations/all/expression_identifiers.csv
    cat "${this_dir}/feeds.csv" >> ../derivations/all/feeds.csv
    cat "${this_dir}/inference_rule_identifiers.csv" >> ../derivations/all/inference_rule_identifiers.csv
done