import csv

import psycopg2
from flask import Flask, render_template

app = Flask(__name__)
FARMS = ['zarya', 'progres', 'druzhba']

def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='db',
                            user='postgres',
                            password='1ZakonOma')
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM volume;')
    books = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', books=books)

def load():
    for farm in FARMS:
        name_volume = farm + '_volume.csv'
        with open(name_volume, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(row['Дата'], row['Площадь, га'], row['Объем работ, м3'])
        name_machine = farm + '_machine.csv'
        with open(name_machine, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(row['Дата'], row['Площадь, га'])

load()