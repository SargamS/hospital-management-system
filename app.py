from flask import Flask, render_template, request, redirect
import sqlite3, os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "hospital.db")
db = sqlite3.connect(db_path, check_same_thread=False)
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

# ------------------ ROUTES ------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        idno = request.form['idno']
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        phone = request.form['phone']
        bg = request.form['bg']

        cursor.execute("INSERT INTO appt VALUES (?, ?, ?, ?, ?, ?)",
                       (idno, name, age, gender, phone, bg))
        db.commit()
        return redirect('/appointments')
    return render_template('register.html')

@app.route('/appointments')
def appointments():
    cursor.execute("SELECT * FROM appt")
    data = cursor.fetchall()
    return render_template('appointments.html', data=data)

@app.route('/doctors')
def doctors():
    return render_template('doctors.html')

@app.route('/services')
def services():
    return render_template('services.html')

# --------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
