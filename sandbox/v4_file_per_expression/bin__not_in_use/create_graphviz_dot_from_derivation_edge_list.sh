output_filename=derivation.dot
temp_outputfile1=temp1.dat
temp_outputfile2=temp2.dat
# cp derivation_edge_list.csv ${output_filename}



while read -r line
do
    echo $line | cut -d',' -f1 >> ${temp_outputfile1} # source
    echo $line | cut -d',' -f2 >> ${temp_outputfile1} # destination
done < derivation_edge_list.csv
cat ${temp_outputfile1} | sort | uniq > ${temp_outputfile2}
# at this point, ${temp_outputfile2} contains all the nodes
rm ${temp_outputfile1}

while read -r node_indx_line
do
    indx_is_feed=yes
    while read -r expr_line
    do
        expr_temp_indx=`echo $expr_line | cut -d',' -f1`
        if [[ $expr_temp_indx == $node_indx_line ]]; then
            expr_perm_indx=`echo $expr_line | cut -d',' -f2`
            echo ${node_indx_line} ${expr_line} >> ${temp_outputfile1}
            indx_is_feed="nope"
        fi    
    done < expression_identifiers.csv
    while read -r infrule_line
    do
        infrule_temp_indx=`echo $line | cut -d',' -f1`
        if [[ $infrule_temp_indx == $node_indx_line ]]; then
            infrule_name=`echo $line | cut -d',' -f2`
            echo ${node_indx_line} ${infrule_name} >> ${temp_outputfile1}
            indx_is_feed="nope"
        fi    
    done < inference_rule_identifiers.csv
    if [[ "${indx_is_feed}" == yes ]]; then
        
    fi
done < ${temp_outputfile2}

# echo "digraph physicsDerivation {" > ${temp_outputfile}
# echo "overlap = false;" >> ${temp_outputfile}
# echo "label=\"Equation relations\\nExtracted from connections_database.csv\";" >> ${temp_outputfile}
# echo "fontsize=12;" >> ${temp_outputfile}
