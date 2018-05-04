#! /usr/bin/env python
#
#   The Simple Secret Sharing Server (SSecretSS)
#       (or, Pygacious, son of Fugacious!)
#   v.0.0.2     2018-04-09
#       Dave Rooney     d@verooney.com
#
#

from flask import Flask, render_template, request, redirect, url_for, g, flash
import sqlite3 as sql 
import datetime as dt
import os, uuid

backend = 'sqlite'      # other backends to come, starting with dynamodb

app = Flask(__name__)
app.config.from_object(__name__)
if os.path.exists(os.path.join(app.instance_path, "config.py")):
    app.config.from_file(os.path.join(app.instance_path, "config.py"))

if backend == 'sqlite':         # maybe move this to config.py once other backends exist
    app.config.update(dict(
        BACKEND='sqlite',
        DATABASE=os.path.join(app.instance_path, 'sssecretss.db'),
        SQLSCHEMA=os.path.join(app.instance_path, 'schema.sql')
    ))
# elif backend == 'other':
#     pass
#     TODO: other backends here
else:
    print "Invalid backend."
    exit

def connect_db():
    if app.config['BACKEND'] == 'sqlite':
        if (os.path.exists(app.config['DATABASE'])):
            db = sql.connect(app.config['DATABASE'])
            db.row_factory = sql.Row
            return db
        else:
            db = sql.connect(app.config['DATABASE'])
#            init_db()
            db.row_factory = sql.Row
            return db
    elif app.config['BACKEND'] == 'other':
       pass 
    else:
        print "Invalid backend."
        exit

def get_db():
    if not hasattr(g, 'db'):
        g.db = connect_db()
        return g.db
    else:
        return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

def init_db():
    db = get_db()
    with app.open_resource(app.config['SQLSCHEMA'], 'r') as f:
        db.cursor().executescript(f.read())
        #
        # For easy reference, the schema is:
        #   drop table if exists secrets;
        #   create table secrets (
        #      id integer primary key autoincrement,
        #      secret_guid text not null,
        #      secret_text text not null,
        #      expire_at text not null,
        #      views_left int not null
        #   );
    db.commit()

@app.cli.command('initsqlite')
def initsqlite_command():
    init_db()
    print("Initialized SQLite database.")

@app.cli.command('expirepass')
def expire_secrets():
    db = get_db()
    now = dt.datetime.now().isoformat()
    timeexp_querytxt = 'DELETE * FROM secrets WHERE expire_at > datetime(?);'
    viewexp_querytxt = 'DELETE * FROM secrets WHERE views_left <= 0;'
    c = db.cursor()
    c.execute(timeexp_querytxt, now)
    c.execute(viewexp_querytxt)
    db.commit()
    c.close()

@app.route('/', methods=["GET", "POST"])
def hello():
    return redirect(url_for('write_secret'))

@app.route('/r/')
def read_nothing():
    return redirect(url_for('write_secret'))

@app.route('/w/', methods=["GET", "POST"])
def write_secret():
    if request.method == "GET":
        pass
    elif request.method == "POST":
        db = get_db()
        secret_guid = uuid.uuid3(uuid.uuid1(),"ssecretss").get_hex()
        now = dt.datetime.now()
        secret_text = request.form["secret_text"]
        expire_after = int(request.form["expire_after"])
        views_allowed = int(request.form["views_allowed"])
        # validation passes
        if len(secret_text) > 1024;
            flash("Secret message is too long! Nope!")
            return redirect(url_for("write_secret"))
        if expire_after > 168:      # 168 hrs = 1 week
            flash("Expiration length is too long! 168 hours is 1 week. Please choose less than a week.")
            return redirect(url_for("write_secret"))
        else:
            expire_at = now + dt.timedelta(hours=expire_after)
        if views_allowed > 10:
            flash("More than 10 views isn't very ephemeral. Please choose fewer.")
            return redirect(url_for("write_secret"))
        db.execute("insert into secrets (secret_guid, secret_text, expire_at, views_left) values (?, ?, ?, ?)", \
            secret_guid, secret_text, expire_at, views_allowed)
        db.commit()
        flash("Your secret has been stashed!")
        return redirect(url_for("read_secret", secretid=secret_guid))
    else:
        abort(405)      # HTTP error code for invalid/disallowed method

@app.route('/r/<secretid>')
def read_secret(secretid):
    db = get_db()
    cur = db.execute("select * from secrets where secret_guid = ?", secretid)
    sec = cur.fetchone()
    dbid, guid, sectext, expire_at, views = sec
    return render_template('main_page.html', secret=sec)

@app.route('/about')
def about():
    pass


if __name__ == "__main__":
    """
    """
    app.run()

