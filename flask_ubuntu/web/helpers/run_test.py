from sqlite_crud import sqlite_crud
x = sqlite_crud()
x.create_table('test',('a','b'))
x.insert('test',('a','b'),(1,2))
x.select('test')
x.drop_table('test')
