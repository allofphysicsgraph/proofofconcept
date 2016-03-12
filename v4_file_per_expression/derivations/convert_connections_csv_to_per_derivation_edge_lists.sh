temp_file=derivation_names.log

cut -f 1 -d ',' ../../../databases/connections_database.csv | uniq > ${temp_file}

while read -r derivation_name_with_quotes
do 
#     echo $derivation_name
    # http://stackoverflow.com/questions/9733338/shell-script-remove-first-and-last-quote-from-a-variable    

    derivation_name="${derivation_name_with_quotes%\"}"     # ${opt%\"} will remove the suffix " (escaped with a backslash to prevent shell interpretation)
    derivation_name="${derivation_name#\"}"    # ${temp#\"} will remove the prefix " (escaped with a backslash to prevent shell interpretation)
    echo $derivation_name
    rm -rf "$derivation_name"
    mkdir "$derivation_name"

    while read -r this_line
    do
#         echo ${this_line}
        this_derivation_in_connections="$( cut -d ',' -f 1 <<< "$this_line" )"
        if [[ ${this_derivation_in_connections} == ${derivation_name_with_quotes} ]]
        then
            step_index="$( cut -d ',' -f 2 <<< "$this_line" )"    
            input_type="$( cut -d ',' -f 3 <<< "$this_line" )"    
            input_temp_id="$( cut -d ',' -f 4 <<< "$this_line" )"    
            input_perm_id="$( cut -d ',' -f 5 <<< "$this_line" )"    
            output_type="$( cut -d ',' -f 6 <<< "$this_line" )"    
            output_temp_id="$( cut -d ',' -f 7 <<< "$this_line" )"    
            output_perm_id="$( cut -d ',' -f 8 <<< "$this_line" )"
                        
#             echo ${derivation_name_with_quotes} ${step_index}
            echo ${input_temp_id},${output_temp_id} >> "$derivation_name"/derivation_edge_list.csv
            
#             echo "input type is " ${input_type}
            
            if [ ${input_type} == '"expression"' ]
            then
                echo ${input_temp_id},${input_perm_id} >> "$derivation_name"/expression_identifiers.csv.tmp
            fi
            if [ ${input_type} == '"infrule"' ]
            then
                echo ${input_temp_id},${input_perm_id} >> "$derivation_name"/inference_rule_identifiers.csv.tmp
            fi
            if [ ${input_type} == '"feed"' ]
            then
                echo ${input_temp_id} >> "$derivation_name"/feeds.csv.tmp
            fi
            if [ ${output_type} == '"expression"' ]
            then
                echo ${output_temp_id},${output_perm_id} >> "$derivation_name"/expression_identifiers.csv.tmp
            fi
            if [ ${output_type} == '"infrule"' ]
            then
                echo ${output_temp_id},${output_perm_id} >> "$derivation_name"/inference_rule_identifiers.csv.tmp
            fi
            
        fi
    done < ../../../databases/connections_database.csv

    cat "$derivation_name"/expression_identifiers.csv.tmp | sort | uniq > "$derivation_name"/expression_identifiers.csv            
    rm "$derivation_name"/expression_identifiers.csv.tmp
    cat "$derivation_name"/inference_rule_identifiers.csv.tmp | sort | uniq > "$derivation_name"/inference_rule_identifiers.csv
    rm "$derivation_name"/inference_rule_identifiers.csv.tmp
    cat "$derivation_name"/feeds.csv.tmp | sort | uniq > "$derivation_name"/feeds.csv
    rm "$derivation_name"/feeds.csv.tmp

done < ${temp_file}