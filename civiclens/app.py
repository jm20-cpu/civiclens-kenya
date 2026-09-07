from flask import Flask, render_template, jsonify, request
import sqlite3, os, math
from datetime import datetime

app=Flask(__name__)
DB=os.getenv('DB_PATH','civiclens.db')

def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init():
    c=db(); c.executescript('''CREATE TABLE IF NOT EXISTS leaders(id INTEGER PRIMARY KEY,name TEXT,office TEXT,county TEXT,party TEXT,performance REAL,activity REAL,promise REAL,budget REAL,evidence REAL);''')
    if c.execute('SELECT COUNT(*) FROM leaders').fetchone()[0]==0:
        rows=[('Sample Leader A','National Office','Kenya','Party A',72,81,68,74,92),('Sample Leader B','County Office','Example County','Party B',65,76,61,79,88),('Sample Leader C','Parliament','Example County','Independent',80,69,73,71,95)]
        c.executemany('INSERT INTO leaders(name,office,county,party,performance,activity,promise,budget,evidence) VALUES(?,?,?,?,?,?,?,?,?)',rows)
    c.commit(); c.close()

def score(r): return round(sum(r[k] for k in ('performance','activity','promise','budget','evidence'))/5,1)

@app.route('/')
def home():
    c=db(); leaders=c.execute('SELECT * FROM leaders ORDER BY performance DESC').fetchall(); c.close()
    return render_template('index.html',leaders=leaders,score=score)

@app.route('/leaders')
def leaders():
    q=request.args.get('q','').strip(); c=db()
    if q: rows=c.execute('SELECT * FROM leaders WHERE name LIKE ? OR county LIKE ? OR party LIKE ?', (f'%{q}%',f'%{q}%',f'%{q}%')).fetchall()
    else: rows=c.execute('SELECT * FROM leaders ORDER BY performance DESC').fetchall()
    c.close(); return render_template('leaders.html',leaders=rows,score=score,q=q)

@app.route('/leader/<int:lid>')
def leader(lid):
    c=db(); r=c.execute('SELECT * FROM leaders WHERE id=?',(lid,)).fetchone(); c.close()
    if not r: return 'Leader not found',404
    return render_template('leader.html',leader=r,score=score(r))

@app.route('/compare')
def compare():
    ids=request.args.getlist('id',type=int); c=db(); rows=[]
    for i in ids[:4]:
        r=c.execute('SELECT * FROM leaders WHERE id=?',(i,)).fetchone()
        if r: rows.append(r)
    c.close(); return render_template('compare.html',leaders=rows,score=score)

@app.route('/api/leaders')
def api():
    c=db(); rows=c.execute('SELECT * FROM leaders ORDER BY performance DESC').fetchall(); c.close()
    return jsonify([dict(r,overall_score=score(r)) for r in rows])

@app.route('/refresh',methods=['POST','GET'])
def refresh():
    return jsonify({'status':'ready','message':'Data refresh pipeline is ready. Connect official source adapters before publishing live political data.','updated_at':datetime.utcnow().isoformat()+'Z'})

init()
if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.getenv('PORT',5000)),debug=True)
