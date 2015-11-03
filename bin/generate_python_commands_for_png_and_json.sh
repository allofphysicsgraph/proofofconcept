# prints the commands for running each and all the derivations

mkdir output
cut -f 1 -d ',' databases/connections_database.csv | uniq > output/list_of_derivations.dat

while read line; do 
    if [[ $line != \" ]]
    then
        echo python bin/build_derivation_png_from_csv.py  $line
        echo python bin/build_derivation_json_from_csv.py $line
    fi
done < output/list_of_derivations.dat

echo  python bin/build_derivation_png_from_csv.py  \"all\"
echo  python bin/build_derivation_json_from_csv.py \"all\"
