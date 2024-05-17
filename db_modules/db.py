import sqlite3

DB = sqlite3.connect("data.db", check_same_thread=False)

def close_connection():
    #Close the database connection.#
    DB.close()

def init_tables():
    #Initialize tables from database_scheme.sql.#
    with open("database_scheme.sql", "r") as init_file:
        init_sql = init_file.read()
    
    cursor = DB.cursor()
    cursor.executescript(init_sql)
    DB.commit()
    cursor.close()

def drop_tables():
    #Drop all tables from the database.#
    cursor = DB.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table[0]};")
    DB.commit()
    cursor.close()

def drop_one_table(table):
    cursor = DB.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table};")
    DB.commit()
    print(f"table {table} dropped")
    cursor.close()

def drop_all_rows(table):
    cursor = DB.cursor()
    cursor.execute(f"DELETE FROM {table};")
    DB.commit()
    print(f"deleted all rows from {table}")
    cursor.close()
