# prints the commands for running each and all the derivations

mkdir output
cut -f 1 -d ',' databases/connections_database.csv | uniq > output/list_of_derivations.dat

script_name_pictures=create_picture_per_derivation_from_connectionsDB.py
script_name_json=create_json_from_csv.py

while read line; do 
    if [[ $line != \" ]]
    then
        echo python bin/${script_name_pictures}  $line
        echo python bin/${script_name_json} $line
    fi
done < output/list_of_derivations.dat

echo  python bin/${script_name_pictures}  \"all\"
echo  python bin/${script_name_json} \"all\"
