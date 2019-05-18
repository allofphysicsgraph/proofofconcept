# https://docs.python.org/3/library/sqlite3.html
import sqlite3
import csv

print('sqlite3 version:',sqlite3.version)

db_file = "sqlite.db"

try:
    conn = sqlite3.connect(db_file)
except sqlite3.Error:
    print(sqlite3.Error)

c = conn.cursor()

try:
    c.execute('''drop table inference_rules''')
except:
    pass
# https://allofphysicsgraph.github.io/proofofconcept/site/how_to_build_the_physics_derivation.html
c.execute('''CREATE TABLE inference_rules
("inference rule abbreviation","number of arguments","number of feeds","number of input expressions","number of output expressions","comments","latex expansion",yyyymmdd,author)''')

# insert many records at a time

inf_rules = []
with open('v3_CSV/databases/inference_rules_database.csv') as fil:
    csv_reader = csv.reader(fil, delimiter=',')
    for line in csv_reader:
        line_as_list = [x.strip() for x in line]
        print(line_as_list)
        line_as_list.append('20190517')
        line_as_list.append('bhpayne')
        inf_rules.append(set(line_as_list))

c.executemany('INSERT INTO inference_rules VALUES (?,?,?,?,?,?,?,?,?)', inf_rules)


c.execute('''CREATE TABLE expressions
             (unique identifier,local identifier,latex)''')

c.execute('''CREATE TABLE feeds
             (local identifier,latex)''')





conn.commit() # Save (commit) the changes

conn.close()

