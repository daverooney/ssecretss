#! /usr/bin/env python
#
#   The Simple Secret Sharing Server (SSecretSS)
#   or, Pygacious, son of Fugacious!
#   v.0.0.2     2018-04-09
#       Dave Rooney     d@verooney.com
#
#

from flask import Flask, render_template
import sqlite3 as sql
import os

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.rootpath, 'sssecretss.db')
))

def connect_db():
    rv = sql.connect(app.config['DATABASE'])
    rv.row_factory = sql.Row
    return rv

@app.route('/', methods=["GET", "POST"])
def hello():
   return render_template("main_page.html")

@app.route('/w/', methods=["POST"])
def stash_secret():
    pass

@app.route('/r/<secretid>')
def flash_secret(secretid):
    pass

@app.route('/about')
def about():
    pass

app.run()

