import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, send_from_directory
import os
from werkzeug import secure_filename
import list_files

#---CONFIG---#
DATABASE = '__sqlite__//webserver.db'
USERNAME = 'federico'
PASSWORD = 'root@this'
SECRET_KEY = 'developement key'
DEBUG=True
UPLOAD_FOLDER = 'files//'
#---CONFIG---#

app=Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db=getattr(g,'db',None)
    if db is not None:
        db.close()

@app.route('/')
def show_entries():
    g.db = sqlite3.connect(app.config['DATABASE'])
    cur = g.db.execute('select id,title,text from entries order by id desc')
    entries = [dict(ids=row[0], title=row[1], text=row[2]) for row in cur.fetchall()]
    if 'user' in session:
        return render_template('show_entries.html',entries=entries,user=session['user'])
    else:
        return render_template('show_entries.html',entries=entries)

@app.route('/add',methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title,text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/up_file',methods=['GET','POST'])
def up_file():
    error=None
    if not session.get('logged_in'):
        abort(401)
    if request.method=='POST':
        if not request.files['file']:
            error='File missing'
        else:
            file=request.files['file']
            if file:
                filename=secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('File saved')
                return redirect(url_for('show_entries'))
    return render_template('upload.html',error=error)





@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            session['user'] = request.form['username']
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/remove',methods=['GET','POST'])
def remove():
    error = None
    if not session.get('logged_in'):
        abort(401)
    if request.method=='POST':
        g.db.execute('delete from entries where id=?',request.form['query'])
        g.db.commit()
        flash('Removed entry')
    return redirect(url_for('show_entries'))

@app.route('/files')
def uploaded_files():
    return render_template('files.html',file_list=list_files.list_files(UPLOAD_FOLDER))


@app.route('/files/<filename>')
def send_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
         
@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    flash('Logged out')
    return redirect(url_for('show_entries'))

if __name__=='__main__':
        app.run(port=int('8080'),host='0.0.0.0')






















