import csv

import psycopg2
from flask import Flask, render_template
from openpyxl import Workbook

app = Flask(__name__)
FARMS = ["zarya", "progres", "druzhba"]


def get_db_connection():
    conn = psycopg2.connect(
        host="localhost", database="db", user="postgres", password="1ZakonOma"
    )
    return conn


@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT v.Дата, m.Техника, m.Номер, v.Площадь, v.Объем, v.Хозяйство
        FROM volume v
        JOIN machine m ON v.Дата = m.Дата
        WHERE v.Хозяйство = m.Хозяйство
        ORDER BY v.Дата;
    """
    )
    data = cur.fetchall()
    cur.execute(
        """
        SELECT v.Дата, SUM(v.Площадь), SUM(v.Объем)
        FROM volume v
        GROUP BY v.Дата
        ORDER BY v.Дата;
    """
    )
    datas = cur.fetchall()
    cur.close()
    conn.close()
    labels = [str(row[0]) for row in datas]
    values = [float(row[2]) for row in datas]
    return render_template("index.html", labels=labels, values=values, datas=data)


@app.route("/zarya")
def zarya():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT v.Дата, m.Техника, m.Номер, v.Площадь, v.Объем, v.Хозяйство
        FROM volume v
        JOIN machine m ON v.Дата = m.Дата
        WHERE v.Хозяйство = m.Хозяйство and v.Хозяйство = 'zarya'
        ORDER BY v.Дата;
    """
    )
    datas = cur.fetchall()
    cur.close()
    conn.close()
    labels = [str(row[0]) for row in datas]
    values = [float(row[4]) for row in datas]
    return render_template("index.html", labels=labels, values=values, datas=datas)

@app.route("/druzhba")
def druzhba():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT v.Дата, m.Техника, m.Номер, v.Площадь, v.Объем, v.Хозяйство
        FROM volume v
        JOIN machine m ON v.Дата = m.Дата
        WHERE v.Хозяйство = m.Хозяйство and v.Хозяйство = 'druzhba'
        ORDER BY v.Дата;
    """
    )
    datas = cur.fetchall()
    cur.close()
    conn.close()
    labels = [str(row[0]) for row in datas]
    values = [float(row[4]) for row in datas]
    return render_template("index.html", labels=labels, values=values, datas=datas)


@app.route("/progres")
def progres():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT v.Дата, m.Техника, m.Номер, v.Площадь, v.Объем, v.Хозяйство
        FROM volume v
        JOIN machine m ON v.Дата = m.Дата
        WHERE v.Хозяйство = m.Хозяйство and v.Хозяйство = 'progres'
        ORDER BY v.Дата;
    """
    )
    datas = cur.fetchall()
    cur.close()
    conn.close()
    labels = [str(row[0]) for row in datas]
    values = [float(row[4]) for row in datas]
    return render_template("index.html", labels=labels, values=values, datas=datas)


def load():
    conn = get_db_connection()
    cur = conn.cursor()
    create_and_clean(cur, conn)
    for farm in FARMS:
        name_volume = "./data/" + farm + "_volume.csv"
        with open(name_volume, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cur.execute(
                    "INSERT INTO volume (Дата, Площадь, Объем, Хозяйство)"
                    f"VALUES ('{row['Дата']}', {row['Площадь, га']}, {row['Объем работ, м3']}, '{farm}');"
                )
                conn.commit()
        name_machine = "./data/" + farm + "_machine.csv"
        with open(name_machine, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row["Название техники"].split()[0]
                number = row["Название техники"].split()[1]
                cur.execute(
                    "INSERT INTO machine (Дата, Техника, Номер, Хозяйство)"
                    f"VALUES ('{row['Дата']}', '{name}', '{number}', '{farm}');"
                )
                conn.commit()
    cur.close()
    conn.close()


def create_and_clean(cur, conn):
    cur.execute("DROP TABLE IF EXISTS machine;")
    cur.execute(
        "CREATE TABLE machine (id serial PRIMARY KEY,"
        "Дата date NOT NULL,"
        "Техника varchar (150) NOT NULL,"
        "Номер varchar (150) NOT NULL,"
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


def get_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT v.Дата, m.Техника, m.Номер, v.Площадь, v.Объем, v.Хозяйство
        FROM volume v
        JOIN machine m ON v.Дата = m.Дата
        WHERE v.Хозяйство = m.Хозяйство
        Order by v.Дата;
    """
    )
    data = cur.fetchall()
    cur.close()
    conn.close()
    table = [
        [
            "Дата",
            "Техника",
            "Номер техники",
            "Площадь, га",
            "Объем работ, м3",
            "Хозяйство",
        ]
    ]
    table.extend(data)
    wb = Workbook()
    ws = wb.active
    for row in table:
        ws.append(row)
    wb.save("Итог.xlsx")


load()
get_table()
