cat ../../v3_CSV/database/inference_rules_database.csv | sed  '/^$/d' |\
while read -r this_line; do 
    infrule_name=`echo $this_line | cut -d',' -f1`
    filename="${infrule_name}_parameters.yaml"
    echo "inf_rule_name: ${infrule_name}" > ${filename}
    num_args=`echo $this_line | cut -d',' -f2`
    echo "number_of_arguments: ${num_args}" >> ${filename}
    num_feeds=`echo $this_line | cut -d',' -f3`
    echo "number_of_feeds: ${num_feeds}" >> ${filename}
    num_input_expr=`echo $this_line | cut -d',' -f4`
    echo "number_of_input_expressions: ${num_input_expr}" >> ${filename}
    num_output_expr=`echo $this_line | cut -d',' -f5`
    echo "number_of_output_expressions: ${num_output_expr}" >> ${filename}
    comments=`echo $this_line | cut -d',' -f6`
    echo "comments: ${comments}" >> ${filename}

done
