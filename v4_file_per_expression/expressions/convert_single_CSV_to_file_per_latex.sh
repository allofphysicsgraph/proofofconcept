# http://stackoverflow.com/questions/924388/sh-read-command-eats-slashes-in-input
while read -r this_line
do 
    echo $this_line
    # https://unix.stackexchange.com/questions/53310/splitting-string-by-the-first-occurrence-of-a-delimiter
    expr_id="$( cut -d ',' -f 1 <<< "$this_line" )"
    expr_latex="$( cut -d ',' -f 2- <<< "$this_line" )"    
    echo ${expr_latex} > "${expr_id}_latex_20151229.tex"
done <  ../../../databases/expressions_database.csv


