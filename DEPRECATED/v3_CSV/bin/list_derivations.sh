#!/bin/bash

echo -e "==== as is: ===="
cut -f 1 -d ',' databases/connections_database.csv | uniq

echo -e "==== with underscore: ===="
# replace space with underscore, remove "
cut -f 1 -d ',' databases/connections_database.csv | uniq | sed -e "s/ /_/g" | sed -e "s/\"//g" 