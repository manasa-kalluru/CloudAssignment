import sqlite3

from flask import Flask, request, g, render_template, send_file

# DATABASE = '/var/www/html/flaskapp/example.db'
DATABASE = '/Users/manasa/Documents/ReqEng/example.db'
app = Flask(__name__)
app.config.from_object(__name__)

def databaseConnect():
    return sqlite3.connect(DATABASE)

def getDBConnection():
    dbaseConnection = getattr(g, 'db', None)
    if dbaseConnection is None:
        dbaseConnection = g.db = databaseConnect()
    return dbaseConnection

@app.teardown_appcontext
def close_connection(exception):
    dbaseConnection = getattr(g, 'db', None)
    if dbaseConnection is not None:
        dbaseConnection.close()

def executeSQLQuery(query, args=()):
    curor = getDBConnection().execute(query, args)
    returnedRows = curor.fetchall()
    curor.close()
    return returnedRows

def commit():
    getDBConnection().commit()

@app.route("/")
def hello():
    executeSQLQuery("Create table IF NOT EXISTS users (username varchar(255), password varchar(255),firstname varchar(255),lastname varchar(255),email varchar(255),count int)")
    return render_template('index.html')

@app.route('/login', methods =['POST', 'GET'])
def login():
    errorMessage = ''
    if request.method == 'POST' and str(request.form['username']) !="" and str(request.form['password']) != "":
        username = str(request.form['username'])
        password = str(request.form['password'])
        queryResult = executeSQLQuery("""SELECT firstname,lastname,email,count  FROM users WHERE Username  = (?) AND Password = (?)""", (username, password ))
        if queryResult:
            for row in queryResult:
                return staticResponsePage(row[0], row[1], row[2], row[3])
        else:
            errorMessage = 'Invalid Credentials !'
    elif request.method == 'POST':
        errorMessage = 'Please enter Credentials'
    return render_template('index.html', message = errorMessage)

@app.route('/registration', methods =['GET', 'POST'])
def registration():
    errorMessage = ''
    if request.method == 'POST' and str(request.form['username']) !="" and str(request.form['password']) !="" and str(request.form['firstname']) !="" and str(request.form['lastname']) !="" and str(request.form['email']) !="":
        username = str(request.form['username'])
        password = str(request.form['password'])
        firstname = str(request.form['firstname'])
        lastname = str(request.form['lastname'])
        email = str(request.form['email'])
        uploaded_file = request.files['textfile']
        if not uploaded_file:
            filename = ""
            word_count = ''
        else :
            filename = uploaded_file.filename
            word_count = getNumberOfWords(uploaded_file)
        result = executeSQLQuery("""SELECT *  FROM users WHERE Username  = (?)""", (username, ))
        if result:
            errorMessage = 'User has already registered!'
        else:
            result1 = executeSQLQuery("""INSERT INTO users (username, password, firstname, lastname, email, count) values (?, ?, ?, ?, ?, ? )""", (username, password, firstname, lastname, email, word_count, ))
            commit()
            result2 = executeSQLQuery("""SELECT firstname,lastname,email,count  FROM users WHERE Username  = (?) AND Password = (?)""", (username, password ))
            if result2:
                for row in result2:
                    return staticResponsePage(row[0], row[1], row[2], row[3])
    elif request.method == 'POST':
        errorMessage = 'Some of the fields are missing!'
    return render_template('registration.html', message = errorMessage)

@app.route("/download")
def download():
    path = "limerick.txt"
    return send_file(path, as_attachment=True)

def getNumberOfWords(file):
    data = file.read()
    words = data.split()
    return str(len(words))

def staticResponsePage(firstname, lastname, email, count):
    return """ First Name :  """ + str(firstname) + """ <br> Last Name : """ + str(lastname) + """ <br> Email : """ + str(email) + """ <br> Word Count : """ + str(count) + """ <br><br> <a href="/download" >Download</a> """

if __name__ == '__main__':
  app.run()