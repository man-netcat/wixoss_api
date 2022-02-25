import sqlite3

from flask import Flask, g, jsonify, request, render_template

app = Flask(__name__)

app.debug = True

valid_args = [
    'class',
    'team',
    'artist',
    'type',
    'flavor_text',
    'level',
    'power_text',
    'rarity',
    'card_text',
    'color',
    'product',
    'grow_cost',
    'timing',
    'power',
    'name',
    'limits',
    'cost',
    'id'
]

special = ['or']


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database.db')
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cards')
def cards():
    cur = get_db().cursor()
    query = 'SELECT * FROM cards'
    query_params = []
    if request.args:
        junction = 'OR' if 'or' in request.args else 'AND'
        query_args = []
        for arg in request.args:
            if arg in special or arg not in valid_args:
                continue
            query_args.append(f"(`{arg}`=?)")
            query_params.append(request.args[arg])
        criterion = f' {junction} '.join(query_args)
        query += " WHERE " + criterion
    cur.execute(query, query_params)
    res = cur.fetchall()
    unpacked = [{k: row[k] for k in row.keys()} for row in res]
    return jsonify(unpacked)


app.run()
