#!/usr/bin/env python
# encoding: utf-8

import logging
import os
import sqlite3

from flask import (Flask, flash, g, jsonify, redirect, render_template,
                   request, send_from_directory, url_for)
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


def exec_query(query, params):
    if type(params) != list:
        params = [params]
    cur = get_db().cursor()
    cur.execute(query, params)
    res = cur.fetchall()
    unpacked = [{k: row[k] for k in row.keys()} for row in res]
    return unpacked


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
def gallery():
    imglist = os.listdir('./static/cardimages/')
    sort_nicely(imglist)
    divided = divide_chunks(imglist, 4)
    return render_template('gallery.html', list=divided)


@app.route('/search', methods=('GET', 'POST'))
def search():
    res = []
    if request.method == 'POST':
        name = request.form['name']
        if name:
            query = "SELECT * FROM cards WHERE name LIKE '%'||?||'%'"
            res = exec_query(query, name)
    return render_template('form.html', results=res)


@app.route('/cards')
def cards():
    query = 'SELECT * FROM cards'
    params = []
    if request.args:
        junction = 'OR' if 'or' in request.args else 'AND'
        args = []
        for arg in request.args:
            if arg in special or arg not in valid_args:
                continue
            args.append(f"(`{arg}` LIKE '%'||?||'%')")
            params.append(request.args[arg])
        criterion = f' {junction} '.join(args)
        query += " WHERE " + criterion
    res = exec_query(query, params)
    return jsonify(res)


if __name__ == '__main__':
    if True:
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
        app.secret_key = "super secret key"
        app.run(host="localhost", port=80, debug=True)
