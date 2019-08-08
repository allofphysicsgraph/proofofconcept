
class sqlite_crud():
    def __init__(self):
        self.db = "sqlite.db"

    def setup_connection(self):
        import sqlite3
        import datetime
        try:
            conn = sqlite3.connect(self.db) 
            cursor = conn.cursor()
            return conn,cursor
        except Exception as e:
            print(e)
    
    def close_connection(self,conn):
        try:
            conn.close()
        except Exception as e:
            print(e)

    def create_table(self,table_name,fields):
        #TODO add check query for basic errors before running
        import re
        conn,cursor = self.setup_connection()
        statement = "CREATE TABLE {} {}".format(table_name,fields)
        try:
            if not re.findall('CREATE TABLE',statement[:12]):
                exit(1)
            cursor.execute(statement)
            conn.commit()
            self.close_connection(conn)
        except Exception as e:
            print(e)
        return

    def select(self,table_name,fields='*',filters=''):
        #TODO sanity check the query
        import re
        conn,cursor = self.setup_connection()
        query = "select {} from {} {}".format(fields,table_name,filters)
        print(query)
        cursor.execute(query)
        resp = cursor.fetchall()
        print(resp)
        self.close_connection(conn)

    def insert(self,table_name,value_columns,values):
        #TODO sanity check the query
        import re
        conn,cursor = self.setup_connection()
        query = """insert into {} {} values {}""".format(table_name,value_columns,values)
        print(query)
        cursor.execute(query)
        conn.commit()
        resp = cursor.fetchall()
        #print(resp)
        self.close_connection(conn)
    
    def update(self):
        pass

    def drop_table(self,table_name):
        import re
        conn,cursor = self.setup_connection()
        statement = "DROP TABLE IF EXISTS {} ".format(table_name)
        #print(statement)
        try:
            if not re.findall('DROP TABLE IF EXISTS',statement[:20]):
                exit(1)
            cursor.execute(statement)
            conn.commit()
            print('table dropped {}'.format(table_name))
            self.close_connection(conn)
        except Exception as e:
            print(e)
        return
        pass

