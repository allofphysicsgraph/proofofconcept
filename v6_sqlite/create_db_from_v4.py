# to run, use
# python3 v6_sqlite/create_db.py

# https://allofphysicsgraph.github.io/proofofconcept/site/how_to_build_the_physics_derivation.html


# https://docs.python.org/3/library/sqlite3.html
import sqlite3
import csv
import glob

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
    print('did not drop table inference_rules')
    pass
# source of schema is v3_CSV/databases/README
c.execute('''CREATE TABLE inference_rules
("inference rule abbreviation","number of arguments","number of feeds","number of input expressions","number of output expressions","comments","latex expansion",yyyymmdd,author,ast)''')


inf_rules = []

list_of_ast_files = glob.glob('../v4_file_per_expression/inference_rules/*.ast')

with open('../v3_CSV/databases/inference_rules_database.csv') as fil:
    csv_reader = csv.reader(fil, delimiter=',')
    for line in csv_reader:
        line_as_list = [x.strip() for x in line]
        #print(line_as_list)
        if (len(line_as_list)==7):
            line_as_list.append('20190617')
            line_as_list.append('bhpayne')
            
            found_ast=False
            for this_ast in list_of_ast_files:
                #print('this_ast=',this_ast.split('/')[-1])
                #print(line_as_list[0])
                if this_ast.split('/')[-1].startswith(line_as_list[0]):
#                    print('found',)
                    with open(this_ast) as ast_fil:
                        ast_content = ast_fil.read()
                        #print(ast_content)
                        found_ast=True
                        line_as_list.append(ast_content)
                        break # only use the first ast
            if not found_ast:
                line_as_list.append('input:\nouput:\n')
            inf_rules.append(tuple(line_as_list))
        elif (len(line_as_list)==0):
            pass # empty line
        else:
            print('ERROR with',line)

c.executemany('INSERT INTO inference_rules VALUES (?,?,?,?,?,?,?,?,?,?)', inf_rules)

try:
    c.execute('''drop table expressions''')
except:
    print('did not drop table expressions')
    pass
c.execute('''CREATE TABLE expressions
             ("unique identifier",latex)''')

list_of_expr_tuples=[]
list_of_expr_files = glob.glob('../v4_file_per_expression/expressions/*.tex')
for expr_file in list_of_expr_files:
    with open(expr_file,'r') as fil:
        latex_expr = fil.read().strip()
    #print(expr_file.split('/')[-1].split('_')[0],':',latex_expr)
    list_of_expr_tuples.append(tuple([expr_file.split('/')[-1].split('_')[0],latex_expr]))
    
c.executemany('INSERT INTO expressions VALUES (?,?)', list_of_expr_tuples)

    
try:
    c.execute('''drop table feeds''')
except:
    print('did not drop table feeds')
    pass
c.execute('''CREATE TABLE feeds
             ("local identifier",latex)''')
list_of_feed_tuples=[]
list_of_feed_files = glob.glob('../v4_file_per_expression/feeds/*.tex')
for feed_file in list_of_feed_files:
    with open(feed_file,'r') as fil:
        latex_feed = fil.read().strip()
    list_of_feed_tuples.append(tuple([feed_file.split('/')[-1].split('_')[0],latex_feed]))
    
c.executemany('INSERT INTO feeds VALUES (?,?)', list_of_feed_tuples)


list_of_derivation_folders = glob.glob('../v4_file_per_expression/derivations/*')
for deriv_folder in list_of_derivation_folders:
    if deriv_folder.split('/')[-1]!='all':
        print('deriv folder =',deriv_folder)

#derivation_edge_list.csv
#expression_identifiers.csv
#feeds.csv
#inference_rule_identifiers.csv
        
        
conn.commit() # Save (commit) the changes

conn.close()

