find derivations identities -name 'inference_rule_identifiers.csv' -exec 'cat' {} \; |\
 cut -d',' -f2 | sort | uniq -c | sort -g -k1,1