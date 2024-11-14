import psycopg2 as pg

conn = None

db_connection_str = "host=localhost user=jinsoo dbname=example password=password port=5432 options='-c search_path=s_2019040591'"

try:
    conn = pg.connect(db_connection_str)
except Exception as err:
    print("Cannot Create DB Connection", err)