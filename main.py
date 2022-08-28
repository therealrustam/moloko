import csv

import psycopg2
from flask import Flask, redirect, render_template, request
from openpyxl import Workbook

app = Flask(__name__)
FARMS = ["zarya", "progres", "druzhba"]
MEMORY = {
    "max": 0,
    "min": 0,
    "farms": [],
}


def get_db_connection():
    conn = psycopg2.connect(
        host="localhost", database="db", user="postgres", password="1ZakonOma"
    )
    return conn


@app.route("/", methods=("GET", "POST"))
def index():
    load()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT MAX(v.Дата), MIN(v.Дата)
        FROM volume v
            """
    )
    data = cur.fetchall()
    date_to_init = data[0][0]
    date_from_init = data[0][1]
    if request.method == "POST":
        date_to = request.form["to"]
        date_from = request.form["from"]
        if not date_to:
            date_to = date_to_init
        if not date_from:
            date_from = date_from_init
    else:
        date_to = date_to_init
        date_from = date_from_init
    cur.execute(
        """
        SELECT v.Дата, m.Техника, m.Номер, v.Площадь, v.Объем, v.Хозяйство
        FROM volume v
        JOIN machine m ON v.Дата = m.Дата
        WHERE v.Хозяйство = m.Хозяйство AND v.Дата <= '%s' AND v.Дата >= '%s'
        ORDER BY v.Дата;
    """
        % (date_to, date_from)
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
    cur.execute(
        """
        SELECT v.Дата, SUM(v.Площадь), SUM(v.Объем)
        FROM volume v
        WHERE v.Дата <= '%s' AND v.Дата >= '%s'
        GROUP BY v.Дата
        ORDER BY v.Дата;
    """
        % (date_to, date_from)
    )
    data_graph = cur.fetchall()
    cur.execute(
        """
        SELECT Sum(v.Объем)
        FROM volume v
        WHERE v.Хозяйство = 'zarya' AND v.Дата <= '%s' AND v.Дата >= '%s'
    """
        % (date_to, date_from)
    )
    zarya_volume = float(cur.fetchall()[0][0])
    cur.execute(
        """
        SELECT Sum(v.Объем)
        FROM volume v
        WHERE v.Хозяйство = 'druzhba' AND v.Дата <= '%s' AND v.Дата >= '%s'
    """
        % (date_to, date_from)
    )
    druzhba_volume = float(cur.fetchall()[0][0])
    cur.execute(
        """
        SELECT Sum(v.Объем)
        FROM volume v
        WHERE v.Хозяйство = 'progres' AND v.Дата <= '%s' AND v.Дата >= '%s'
        """
        % (date_to, date_from)
    )
    progres_volume = float(cur.fetchall()[0][0])
    cur.close()
    conn.close()
    labels = [str(row[0]) for row in datas]
    values = [float(row[2]) for row in datas]
    label_graph = [str(row[0]) for row in data_graph]
    value_graph = [float(row[2]) for row in data_graph]
    MEMORY["max"] = date_to
    MEMORY["min"] = date_from
    MEMORY["farms"] = ["'zarya'", "'progres'", "'druzhba'"]
    return render_template(
        "index.html",
        labels=labels,
        values=values,
        datas=data,
        zarya_volume=zarya_volume,
        progres_volume=progres_volume,
        druzhba_volume=druzhba_volume,
        label_graph=label_graph,
        value_graph=value_graph,
    )


@app.route("/zarya", methods=("GET", "POST"))
def zarya():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT MAX(v.Дата), MIN(v.Дата)
        FROM volume v
        WHERE v.Хозяйство = 'zarya'
        """
    )
    data = cur.fetchall()
    date_to_init = data[0][0]
    date_from_init = data[0][1]
    if request.method == "POST":
        date_to = request.form["to"]
        date_from = request.form["from"]
        if not date_to:
            date_to = date_to_init
        if not date_from:
            date_from = date_from_init
    else:
        date_to = date_to_init
        date_from = date_from_init
    cur.execute(
        """
        SELECT v.Дата, m.Техника, m.Номер, v.Площадь, v.Объем, v.Хозяйство
        FROM volume v
        JOIN machine m ON v.Дата = m.Дата
        WHERE v.Хозяйство = m.Хозяйство AND v.Хозяйство = 'zarya'
        ORDER BY v.Дата;
        """
    )
    datas = cur.fetchall()
    labels = [str(row[0]) for row in datas]
    values = [float(row[4]) for row in datas]
    cur.execute(
        """
        SELECT v.Дата, m.Техника, m.Номер, v.Площадь, v.Объем, v.Хозяйство
        FROM volume v
        JOIN machine m ON v.Дата = m.Дата
        WHERE v.Хозяйство = m.Хозяйство AND v.Хозяйство = 'zarya' AND v.Дата <= '%s' AND v.Дата >= '%s'
        ORDER BY v.Дата;
        """
        % (date_to, date_from)
    )
    datas = cur.fetchall()
    label_graph = [str(row[0]) for row in datas]
    value_graph = [float(row[4]) for row in datas]
    cur.close()
    conn.close()
    MEMORY["max"] = date_to
    MEMORY["min"] = date_from
    MEMORY["farms"] = ["'zarya'"]
    return render_template(
        "farm.html",
        label_graph=label_graph,
        value_graph=value_graph,
        datas=datas,
        labels=labels,
        values=values,
    )


@app.route("/druzhba", methods=("GET", "POST"))
def druzhba():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT MAX(v.Дата), MIN(v.Дата)
        FROM volume v
        WHERE v.Хозяйство = 'druzhba'
        """
    )
    data = cur.fetchall()
    date_to_init = data[0][0]
    date_from_init = data[0][1]
    if request.method == "POST":
        date_to = request.form["to"]
        date_from = request.form["from"]
        if not date_to:
            date_to = date_to_init
        if not date_from:
            date_from = date_from_init
    else:
        date_to = date_to_init
        date_from = date_from_init
    cur.execute(
        """
        SELECT v.Дата, m.Техника, m.Номер, v.Площадь, v.Объем, v.Хозяйство
        FROM volume v
        JOIN machine m ON v.Дата = m.Дата
        WHERE v.Хозяйство = m.Хозяйство AND v.Хозяйство = 'druzhba'
        ORDER BY v.Дата;
        """
    )
    datas = cur.fetchall()
    labels = [str(row[0]) for row in datas]
    values = [float(row[4]) for row in datas]
    cur.execute(
        """
        SELECT v.Дата, m.Техника, m.Номер, v.Площадь, v.Объем, v.Хозяйство
        FROM volume v
        JOIN machine m ON v.Дата = m.Дата
        WHERE v.Хозяйство = m.Хозяйство AND v.Хозяйство = 'druzhba' AND v.Дата <= '%s' AND v.Дата >= '%s'
        ORDER BY v.Дата;
        """
        % (date_to, date_from)
    )
    datas = cur.fetchall()
    label_graph = [str(row[0]) for row in datas]
    value_graph = [float(row[4]) for row in datas]
    cur.close()
    conn.close()
    MEMORY["max"] = date_to
    MEMORY["min"] = date_from
    MEMORY["farms"] = ["'druzhba'"]
    return render_template(
        "farm.html",
        label_graph=label_graph,
        value_graph=value_graph,
        datas=datas,
        labels=labels,
        values=values,
    )


@app.route("/progres", methods=("GET", "POST"))
def progres():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT MAX(v.Дата), MIN(v.Дата)
        FROM volume v
        WHERE v.Хозяйство = 'progres'
        """
    )
    data = cur.fetchall()
    date_to_init = data[0][0]
    date_from_init = data[0][1]
    if request.method == "POST":
        date_to = request.form["to"]
        date_from = request.form["from"]
        if not date_to:
            date_to = date_to_init
        if not date_from:
            date_from = date_from_init
    else:
        date_to = date_to_init
        date_from = date_from_init
    cur.execute(
        """
        SELECT v.Дата, m.Техника, m.Номер, v.Площадь, v.Объем, v.Хозяйство
        FROM volume v
        JOIN machine m ON v.Дата = m.Дата
        WHERE v.Хозяйство = m.Хозяйство AND v.Хозяйство = 'progres'
        ORDER BY v.Дата;
    """
    )
    datas = cur.fetchall()
    labels = [str(row[0]) for row in datas]
    values = [float(row[4]) for row in datas]
    cur.execute(
        """
        SELECT v.Дата, m.Техника, m.Номер, v.Площадь, v.Объем, v.Хозяйство
        FROM volume v
        JOIN machine m ON v.Дата = m.Дата
        WHERE v.Хозяйство = m.Хозяйство AND v.Хозяйство = 'progres' AND v.Дата <= '%s' AND v.Дата >= '%s'
        ORDER BY v.Дата;
        """
        % (date_to, date_from)
    )
    datas = cur.fetchall()
    label_graph = [str(row[0]) for row in datas]
    value_graph = [float(row[4]) for row in datas]
    cur.close()
    conn.close()
    MEMORY["max"] = date_to
    MEMORY["min"] = date_from
    MEMORY["farms"] = ["'progres'"]
    return render_template(
        "farm.html",
        label_graph=label_graph,
        value_graph=value_graph,
        datas=datas,
        labels=labels,
        values=values,
    )


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


@app.route("/get")
def get_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT v.Дата, m.Техника, m.Номер, v.Площадь, v.Объем, v.Хозяйство
        FROM volume v
        JOIN machine m ON v.Дата = m.Дата
        WHERE v.Хозяйство = m.Хозяйство AND v.Хозяйство IN (%s) AND v.Дата <= '%s' AND v.Дата >= '%s'
        Order by v.Дата;
    """
        % (",".join(MEMORY["farms"]), MEMORY["max"], MEMORY["min"])
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
    return redirect("/")
