cut -f 1 -d ',' databases/connections_database.csv | uniq > temp.dat

while read line; do 
    if [[ $line != \" ]]
    then
        echo python bin/build_derivation_png_from_csv.py  $line
        echo python bin/build_derivation_json_from_csv.py $line
    fi
done < temp.dat

echo  python bin/build_derivation_png_from_csv.py  \"all\"
echo  python bin/build_derivation_json_from_csv.py \"all\"
