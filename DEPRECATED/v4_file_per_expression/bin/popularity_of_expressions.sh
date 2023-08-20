find derivations identities -name 'expression_identifiers.csv' -exec 'cat' {} \; |\
 cut -d',' -f2  | xargs -I % sh -c 'cat expressions/%_latex_*' | sort | uniq -c | sort -g -k1,1
 
# find derivations identities -name 'expression_identifiers.csv' -exec 'cat' {} \; |\
# cut -d',' -f2  | sort | uniq -c | sort -g -k1,1