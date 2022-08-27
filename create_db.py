import psycopg2

conn = psycopg2.connect(
    host="localhost", database="db", user="postgres", password="1ZakonOma"
)


cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS machine;")
cur.execute(
    "CREATE TABLE machine (id serial PRIMARY KEY,"
    "Дата date NOT NULL,"
    "Название varchar (150) NOT NULL,"
    "Хозяйство varchar (150) NOT NULL);"
)

cur.execute("DROP TABLE IF EXISTS volume;")
cur.execute(
    "CREATE TABLE volume (id serial PRIMARY KEY,"
    "Дата date NOT NULL,"
    "Площадь decimal NOT NULL,"
    "Объем decimal NOT NULL,"
    "Хозяйство varchar (150) NOT NULL);"
)

conn.commit()
cur.close()
conn.close()
