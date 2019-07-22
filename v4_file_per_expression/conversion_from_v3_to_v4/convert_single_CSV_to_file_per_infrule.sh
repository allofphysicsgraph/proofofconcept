# http://stackoverflow.com/questions/924388/sh-read-command-eats-slashes-in-input
while read -r this_line
do 
    echo $this_line
    # https://unix.stackexchange.com/questions/53310/splitting-string-by-the-first-occurrence-of-a-delimiter
    expr_id="$( cut -d ',' -f 1 <<< "$this_line" )"
    expr_latex="$( cut -d ',' -f 7- <<< "$this_line" )"    

    # http://stackoverflow.com/questions/9733338/shell-script-remove-first-and-last-quote-from-a-variable    
    expr_latex="${expr_latex%\"}"     # ${opt%\"} will remove the suffix " (escaped with a backslash to prevent shell interpretation)
    expr_latex="${expr_latex#\"}"    # ${temp#\"} will remove the prefix " (escaped with a backslash to prevent shell interpretation)

    echo ${expr_latex} > "${expr_id}_latex_20151229.tex"
done <  ../../../databases/inference_rules_database.csv


