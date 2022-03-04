#!/usr/bin/env python
# encoding: utf-8

import logging
import os
import sqlite3

from flask import (Flask, g, jsonify, render_template, request,
                   send_from_directory)
from waitress import serve

from misc.tools import divide_chunks, sort_nicely

app = Flask(__name__)


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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/img/<path:filename>')
def image(filename):
    return send_from_directory('./static/cardimages/', f'{filename}'), 200


@app.route('/img')
def imgdir():
    imglist = os.listdir('./static/cardimages/')
    sort_nicely(imglist)
    divided = divide_chunks(imglist, 4)
    return render_template('imgdir.html', list=divided)


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
            query_args.append(f"(`{arg}` LIKE '%'||?||'%')")
            query_params.append(request.args[arg])
        criterion = f' {junction} '.join(query_args)
        query += " WHERE " + criterion
    cur.execute(query, query_params)
    res = cur.fetchall()
    unpacked = [{k: row[k] for k in row.keys()} for row in res]
    return jsonify(unpacked)


if __name__ == '__main__':
    if False:
        serve(
            app,
            host="0.0.0.0",
            port=80,
            url_scheme='https',
            threads=8,
        )
        logger = logging.getLogger('waitress')
        logger.setLevel(logging.INFO)
    else:
        app.run(host="localhost", port=80, debug=True)
