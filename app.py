from flask import Flask, render_template, request, redirect
import sqlite3

# Create (or connect) to local SQLite database file
db = sqlite3.connect("hospital.db", check_same_thread=False)
cursor = db.cursor()

# Create table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS appt(
    idno TEXT PRIMARY KEY,
    name TEXT,
    age INTEGER,
    gender TEXT,
    phone TEXT,
    bg TEXT
)
''')
db.commit()


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/doctors')
def doctors():
    cursor.execute("SELECT * FROM doctor_list")
    doctors = cursor.fetchall()
    return render_template('doctors.html', doctors=doctors)

@app.route('/services')
def services():
    cursor.execute("SELECT * FROM services_list")
    services = cursor.fetchall()
    return render_template('services.html', services=services)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        idno = request.form['idno']
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        phone = request.form['phone']
        bg = request.form['bg']
        cursor.execute("INSERT INTO appt VALUES (%s,%s,%s,%s,%s,%s)", (idno,name,age,gender,phone,bg))
        db.commit()
        return redirect('/')
    return render_template('register.html')

@app.route('/appointments')
def appointments():
    cursor.execute("SELECT * FROM appt")
    data = cursor.fetchall()
    return render_template('appointments.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
