import sqlite3

from flask import Flask, g, jsonify, request

app = Flask(__name__)

valid_args = {
    "id": "Card Id",
    "level": "Level",
    "limits": "Limits",
    "type": "Card Type",
    "class": "LRIG Type/Class",
    "rarity": "Rarity",
    "color": "Color",
    "colour": "Color",
}

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
    return """<h1>Search a card by id by using /cards</h1><p>Accepted arguments are: id, level, limits, type, class, rarity and color.</p><p>For disjunctive search, use &or</p>"""


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
            query_args.append(f"(`{valid_args[arg]}`=?)")
            query_params.append(request.args[arg])
        criterion = f' {junction} '.join(query_args)
        query += " WHERE " + criterion
    cur.execute(query, query_params)
    res = cur.fetchall()
    unpacked = [{k: row[k] for k in row.keys()} for row in res]
    return jsonify(unpacked)


app.run()
