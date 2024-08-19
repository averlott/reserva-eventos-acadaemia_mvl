
from flask import Flask, request, redirect, url_for, render_template, session, flash, get_flashed_messages
from functools import wraps
import mysql.connector
from mysql.connector import Error
import mysqlcreds as mycreds

app = Flask(__name__)
app.secret_key = 'reservas1234'

def connect_db():
    return mysql.connector.connect(
        host = mycreds.host
        ,user = mycreds.user
        ,password = mycreds.password
        ,database = mycreds.database
    )

def init_db():
    with connect_db() as db:
        cursor = db.cursor()
        db.commit()

def isLoggedIn(f):
    @wraps(f)
    def check(*args, **kwargs):
        if session.get('id'):
            return f(*args, **kwargs)
        else:
            errormessage = "Acceso denegado: deber estar logueado para acceder."
            return render_template("error.html", errormessage=errormessage)
    return check

def isAdmin(f):
    @wraps(f)
    def check(*args, **kwargs):
        if session.get('admin') == 1:
            return f(*args, **kwargs)
        else:
            errormessage = "Acceso denegado: debe ser admin para acceder."
            return render_template("error.html", errormessage=errormessage)
    return check


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form['action']
        if action == 'login':
            email = request.form['email']
            password = request.form['password']
            if check_credentials(email, password):
                #return redirect(url_for('booking'))
                return redirect(url_for('home'))
            else:
                #return redirect(url_for('error'))
                errormessage = "Credenciales incorrectas: verifique el email y pwd ingresado previamente."
                return render_template("error.html", errormessage=errormessage)
        elif action == 'register':
            return redirect(url_for('register'))
        # elif action == 'logout':
        #     return redirect(url_for('logout_user'))
    return render_template('index.html')

def check_credentials(email, password):
  with connect_db() as db:
        cursor = db.cursor()
        cursor.execute('SELECT id, name, email FROM users WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        if user:
            session['admin'] = 0
            session['id'] = user[0]
            session['name'] = user[1]
            session['email'] = user[2]
            session['userPK'] = user[2]
        return user is not None
  
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        with connect_db() as db:
            cursor = db.cursor()
            cursor.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)',
                           (name,email, password))
            db.commit()
        return redirect(url_for('index'))
    return render_template('register.html')

# To redirect To booking Page
@app.route('/booking')
@isLoggedIn
def booking():
    return render_template('booking.html')

def search_events(id):
    try:
        db = connect_db()
        cursor = db.cursor()
        if id == "":
            query = ("SELECT id, name, type, price FROM events")
        else:
            query = ("SELECT id, name, type, price FROM events WHERE id = " + id)
        
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        db.close()
        return records

    except Error as e:
        print("Error conexion MySQL", e)
        return []
    
def check_seat_availability(name):
    with connect_db() as db:
        cursor = db.cursor()
        cursor.execute('SELECT SUM(seats) FROM bookings WHERE name = %s', (name,))
        seats = cursor.fetchone()[0] or 0  
    return seats

@app.route('/book', methods=['POST'])
def book():
    Name = session.get('name')
    Email = session.get('email')
    name = request.form['name']
    type = request.form['type']
    seats = int(request.form['seats_book'])
    price = float(request.form['price'])
    
    booked = check_seat_availability(name)
    max_seats = 40 

    if booked + seats > max_seats:
        flash("Capacidad completada.")
        return redirect(url_for('error')) 
    
    with connect_db() as db:
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO bookings (name, type, seats, price) VALUES (%s, %s, %s, %s)',
            (name, type, seats, price)
        )
        db.commit()

    session['booking'] = {
        'Email': Email,
        'Name': Name,
        'name': name,
        'type': type,
        'seats': seats,
        'price': f"$ {price * seats}"
    }

    return redirect(url_for('confirm'))

@app.route('/confirm')
def confirm():
    booking = session.get('booking', {})
    return render_template('confirm.html', **booking)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/events')
def events():
    records = search_events("")
    if not records:
        flash("No existen eventos. Por favor intente luego.")
        return redirect(url_for('error'))
    return render_template('events.html', records=records)

@app.route('/event', methods=['POST'])
@isLoggedIn
def event():
    id = request.form['id']
    records = search_events(id)
    if not records:
        flash("No existe eventos. Por favor intente luego.")
        return redirect(url_for('error'))
    return render_template('event.html', records=records)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/home')
def home():
    return render_template('index.html')

def check_admin(email, password):
  with connect_db() as db:
        cursor = db.cursor()
        cursor.execute('SELECT id, username, password FROM admins WHERE username = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        if user:
            session['admin'] = 1           
            session['id'] = user[0]
            session['adminPK'] = user[1]
            session['pwd'] = user[2]
        return user is not None

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        action = request.form['action']
        if action == 'login':
            username = request.form['username']
            password = request.form['password']
            if check_admin(username, password):
                return redirect(url_for('adm'))
            else:
                #return redirect(url_for('error'))
                errormessage = "Credenciales incorrectas: verifique el usuario y pwd ingresado previamente."
                return render_template("error.html", errormessage=errormessage)
        elif action == 'register':
            return redirect(url_for('register'))
        # elif action == 'logout':
        #     return redirect(url_for('logout_admin'))
    return render_template('index.html')

@app.route('/addEvent', methods=['GET', 'POST'])
@isAdmin
@isLoggedIn
def addEvent():
    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']
        capacity = request.form['capacity']
        price = request.form['price']
        with connect_db() as db:
            cursor = db.cursor()
            cursor.execute('INSERT INTO events (name, type, capacity, price) VALUES (%s, %s, %s, %s)',
                           (name,type,capacity,price))
            db.commit()
        return redirect(url_for('addEvent'))

    with connect_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT name, type, capacity, price FROM events")
        events = cursor.fetchall()

    return render_template('addEvent.html', events=events)

@app.route("/logout_admin")
def logout_admin():
    session.clear()
    return redirect(url_for('adm'))

@app.route("/logout_user")
def logout_user():
    session.clear()
    return redirect(url_for('home'))

@app.route('/adm')
def adm():
    return render_template('admin.html')

@app.route('/error')
def error():
    return render_template("error.html")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)