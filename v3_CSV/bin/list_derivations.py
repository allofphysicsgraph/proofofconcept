import re

f = open('../databases/connections_database.csv')

resp = sorted(
    set(
        [
            filter(None, re.split('"', row))[0] for row in f.readlines()
        ]
    ))


for row in resp:
    print row


for row in resp:
    print row.strip().replace(' ','_')