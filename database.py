import sqlite3
from sqlite3 import Error
from os.path import isfile

class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        self.tables = None

    def create_connection(self):
        # print("[INFO] Connecting with database " + self.db_file)
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.cursor = self.conn.cursor()
            # print(f"[SUCCESS]::Conection succesfull\n")
        except Error as e:
            print(e)

    def close(self):
        self.conn.close()
        self.conn = None
        self.cursor = None

    def save(self, sql=None):
        if sql:
            self.cursor.execute(sql)
        self.conn.commit()
        self.close()
        self.get_tables()

    def create_table(self, name: str, cols: tuple):
        if not self.conn:
            self.create_connection()

        sql_command = f"CREATE TABLE IF NOT EXISTS {name} (\n"
        for col in cols:
            sql_command += col + ",\n"

        sql_command = sql_command[:-2] + ");"
        self.save(sql_command)
        print(f"[INFO]:: {name.upper()} table created")


    def insert(self, table_name: str, data: tuple):
        self.create_connection()
        sql = f"INSERT INTO {table_name}(\n"
        for item in data:
            name, _ = item
            sql += name + ',\n'
        sql = sql[:-2] + ')\nVALUES('

        for item in data:
            _, value = item
            sql += f"'{value}'" + ',\n'
        sql = sql[:-2] + ");"
        self.save(sql)

    def select(self, table: str):
        pass



    def get_tables(self):
        self.create_connection()
        self.cursor.execute('SELECT name from sqlite_master where type= "table"')
        self.tables = db.cursor.fetchall()
        self.close()

    def drop_table(self, name: str):
        self.create_connection()
        sql = 'drop table if exists ' + name
        self.save(sql)

    def check_if_row_exists(self, table: str, column: str, value: str):
        self.create_connection()
        self.cursor.execute(f"SELECT rowid FROM {table} WHERE {column} = ?", (value,))
        data=self.cursor.fetchall()
        self.save()
        if len(data)==0:
            return False
        else:
            return True





db = Database("game.db")
db.create_connection()
db.create_table('users',
                ('id integer PRIMARY KEY',
                'nick text NOT NULL',
                'score integer'
                ))