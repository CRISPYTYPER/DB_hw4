import psycopg2 as pg

conn = None

# TODO: Override connection info

db_connection_str = "host=localhost user=jinsoo dbname=postgres password=cookie3456!! port=5432"

try:
    conn = pg.connect(db_connection_str)
except Exception as err:
    print("Cannot Create DB Connection", err)