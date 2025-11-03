from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3, os, datetime, json
from decimal import Decimal

app = Flask(__name__)
app.secret_key = "replace-with-a-secure-secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "hospital.db")

# SQLite connection (thread-safe setting for Flask dev)
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# ---------- CREATE ALL REQUIRED TABLES ----------
cur.executescript("""
CREATE TABLE IF NOT EXISTS patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    gender TEXT,
    phone TEXT,
    address TEXT,
    disease TEXT
);

CREATE TABLE IF NOT EXISTS doctors (
    doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    specialization TEXT,
    phone TEXT,
    email TEXT
);

CREATE TABLE IF NOT EXISTS nurses (
    nurse_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    assigned_to INTEGER,
    shift TEXT
);

CREATE TABLE IF NOT EXISTS medicines (
    med_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    quantity INTEGER,
    price REAL
);

CREATE TABLE IF NOT EXISTS facilities (
    bed_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_no TEXT,
    bed_type TEXT,
    availability TEXT,
    patient_id TEXT
);

CREATE TABLE IF NOT EXISTS canteen_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price REAL
);

CREATE TABLE IF NOT EXISTS canteen_orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT,
    items TEXT,
    total REAL,
    status TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS bills (
    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT,
    items TEXT,
    total REAL,
    date TEXT
);
""")
conn.commit()


# ---------------- Helper functions ----------------

def query_all(query, params=()):
    cur.execute(query, params)
    return cur.fetchall()

def query_one(query, params=()):
    cur.execute(query, params)
    return cur.fetchone()

def execute(query, params=()):
    cur.execute(query, params)
    conn.commit()
    return cur.lastrowid


# ✅ FIXED: dashboard_counts uses correct tables
def dashboard_counts():
    total_patients = query_one("SELECT COUNT(*) AS c FROM patients")["c"]
    total_doctors = query_one("SELECT COUNT(*) AS c FROM doctors")["c"]
    total_nurses = query_one("SELECT COUNT(*) AS c FROM nurses")["c"]
    total_medicines = query_one("SELECT COUNT(*) AS c FROM medicines")["c"]
    occupied_beds = query_one("SELECT COUNT(*) AS c FROM facilities WHERE availability='occupied'")["c"]
    available_beds = query_one("SELECT COUNT(*) AS c FROM facilities WHERE availability='available'")["c"]
    return dict(
        patients=total_patients,
        doctors=total_doctors,
        nurses=total_nurses,
        medicines=total_medicines,
        occupied_beds=occupied_beds,
        available_beds=available_beds
    )


# ---------------- Routes ----------------

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/dashboard')
def dashboard():
    counts = dashboard_counts()
    medicine_stock = query_all("SELECT name, quantity FROM medicines ORDER BY med_id DESC LIMIT 8")
    med_labels = [r["name"] for r in medicine_stock]
    med_values = [r["quantity"] for r in medicine_stock]

    total_revenue_row = query_one("SELECT SUM(total) as s FROM bills")
    total_revenue = float(total_revenue_row["s"]) if total_revenue_row["s"] is not None else 0.0

    return render_template(
        "dashboard.html",
        counts=counts,
        med_labels=json.dumps(med_labels),
        med_values=json.dumps(med_values),
        total_revenue=total_revenue
    )


# --------- Patients -----------
@app.route('/patients')
def patients():
    data = query_all("SELECT * FROM patients ORDER BY patient_id DESC")
    return render_template('patients.html', data=data)


@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        phone = request.form['phone']
        address = request.form['address']
        disease = request.form['disease']

        execute(
            "INSERT INTO patients (name, age, gender, phone, address, disease) VALUES (?, ?, ?, ?, ?, ?)",
            (name, age, gender, phone, address, disease)
        )
        flash("Patient added successfully", "success")
        return redirect(url_for('patients'))
    return render_template('add_patient.html')


@app.route('/delete_registered_patient/<int:id>')
def delete_registered_patient(id):
    execute("DELETE FROM patients WHERE patient_id=?", (id,))
    flash("Patient deleted successfully", "success")
    return redirect(url_for('patients'))


# --------- Doctors -----------
@app.route('/doctors')
def doctors():
    rows = query_all("SELECT * FROM doctors ORDER BY name")
    return render_template("doctors.html", doctors=rows)


@app.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        name = request.form['name']
        specialization = request.form['specialization']
        phone = request.form['phone']
        email = request.form['email']
        execute("INSERT INTO doctors (name,specialization,phone,email) VALUES (?, ?, ?, ?)",
                (name, specialization, phone, email))
        flash("Doctor added", "success")
        return redirect(url_for('doctors'))
    return render_template("add_doctor.html")


@app.route('/doctor/<int:doc_id>/delete', methods=['POST'])
def delete_doctor(doc_id):
    execute("DELETE FROM doctors WHERE doc_id = ?", (doc_id,))
    flash("Doctor removed", "success")
    return redirect(url_for('doctors'))


# --------- Nurses -----------
@app.route('/nurses')
def nurses():
    rows = query_all("""
        SELECT n.nurse_id, n.name, n.shift, n.assigned_to, d.name as doctor_name
        FROM nurses n LEFT JOIN doctors d ON n.assigned_to = d.doc_id
        ORDER BY n.name
    """)
    return render_template("nurses.html", nurses=rows, doctors=query_all("SELECT * FROM doctors"))


@app.route('/add_nurse', methods=['GET', 'POST'])
def add_nurse():
    if request.method == 'POST':
        name = request.form['name']
        assigned_to = request.form.get('assigned_to') or None
        assigned_to = int(assigned_to) if assigned_to else None
        shift = request.form['shift']
        execute("INSERT INTO nurses (name, assigned_to, shift) VALUES (?, ?, ?)", (name, assigned_to, shift))
        flash("Nurse added", "success")
        return redirect(url_for('nurses'))
    return render_template("add_nurse.html", doctors=query_all("SELECT * FROM doctors"))


# --------- Facilities / Beds -----------
@app.route('/facilities')
def facilities():
    beds = query_all("SELECT * FROM facilities ORDER BY room_no, bed_id")
    return render_template("facilities.html", beds=beds)


@app.route('/add_bed', methods=['GET', 'POST'])
def add_bed():
    if request.method == 'POST':
        room_no = request.form['room_no']
        bed_type = request.form['bed_type']
        execute("INSERT INTO facilities (room_no, bed_type, availability) VALUES (?, ?, ?)",
                (room_no, bed_type, 'available'))
        flash("Bed added", "success")
        return redirect(url_for('facilities'))
    return render_template("add_bed.html")


@app.route('/assign_bed', methods=['POST'])
def assign_bed():
    bed_id = int(request.form['bed_id'])
    patient_id = request.form['patient_id'].strip()
    bed = query_one("SELECT * FROM facilities WHERE bed_id = ?", (bed_id,))
    if bed and bed['availability'] == 'available':
        execute("UPDATE facilities SET availability=?, patient_id=? WHERE bed_id=?",
                ('occupied', patient_id, bed_id))
        flash("Bed assigned", "success")
    else:
        flash("Bed not available", "danger")
    return redirect(url_for('facilities'))


@app.route('/release_bed/<int:bed_id>', methods=['POST'])
def release_bed(bed_id):
    execute("UPDATE facilities SET availability='available', patient_id=NULL WHERE bed_id=?", (bed_id,))
    flash("Bed released", "success")
    return redirect(url_for('facilities'))


# --------- Pharmacy / Medicines -----------
@app.route('/pharmacy')
def pharmacy():
    meds = query_all("SELECT * FROM medicines ORDER BY name")
    return render_template("pharmacy.html", medicines=meds)


@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        execute("INSERT INTO medicines (name, quantity, price) VALUES (?, ?, ?)", (name, quantity, price))
        flash("Medicine added", "success")
        return redirect(url_for('pharmacy'))
    return render_template("add_medicine.html")


@app.route('/buy_medicine', methods=['POST'])
def buy_medicine():
    med_id = int(request.form['med_id'])
    qty = int(request.form['quantity'])
    med = query_one("SELECT * FROM medicines WHERE med_id = ?", (med_id,))
    if not med:
        flash("Medicine not found", "danger")
    else:
        if med['quantity'] >= qty:
            new_qty = med['quantity'] - qty
            execute("UPDATE medicines SET quantity=? WHERE med_id=?", (new_qty, med_id))
            desc = f"Medicine: {med['name']} x{qty}"
            amount = float(med['price']) * qty
            execute("INSERT INTO bills (patient_id, items, total, date) VALUES (?, ?, ?, ?)",
                    ('store', json.dumps([dict(desc=desc, amount=amount)]),
                     amount, datetime.datetime.now().isoformat()))
            flash("Medicine purchased", "success")
        else:
            flash("Insufficient stock", "danger")
    return redirect(url_for('pharmacy'))


# --------- Canteen (Food ordering) -----------
@app.route('/canteen')
def canteen():
    items = query_all("SELECT * FROM canteen_items ORDER BY name")
    recent_orders = query_all("SELECT * FROM canteen_orders ORDER BY created_at DESC LIMIT 10")
    return render_template("canteen.html", items=items, orders=recent_orders)


@app.route('/add_canteen_item', methods=['POST'])
def add_canteen_item():
    name = request.form['name']
    price = float(request.form['price'])
    execute("INSERT INTO canteen_items (name, price) VALUES (?, ?)", (name, price))
    flash("Canteen item added", "success")
    return redirect(url_for('canteen'))


@app.route('/order_food', methods=['GET', 'POST'])
def order_food():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        items = []
        total = 0.0
        for k, v in request.form.items():
            if k.startswith('item_') and v and int(v) > 0:
                item_id = int(k.split('_', 1)[1])
                qty = int(v)
                item_row = query_one("SELECT * FROM canteen_items WHERE item_id = ?", (item_id,))
                if item_row:
                    subtotal = float(item_row['price']) * qty
                    items.append(dict(item_id=item_id, name=item_row['name'], qty=qty,
                                      price=float(item_row['price']), subtotal=subtotal))
                    total += subtotal
        if not items:
            flash("No items selected", "danger")
            return redirect(url_for('canteen'))
        execute("INSERT INTO canteen_orders (patient_id, items, total, status, created_at) VALUES (?, ?, ?, ?, ?)",
                (patient_id, json.dumps(items), total, 'placed', datetime.datetime.now().isoformat()))
        flash("Order placed", "success")
        return redirect(url_for('canteen'))
    items = query_all("SELECT * FROM canteen_items ORDER BY name")
    return render_template("order_food.html", items=items)


# --------- Billing -----------
@app.route('/billing', methods=['GET', 'POST'])
def billing():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        lines = []
        total = 0.0
        n = int(request.form.get('line_count', '0'))
        for i in range(1, n + 1):
            desc = request.form.get(f'desc_{i}')
            amt = float(request.form.get(f'amt_{i}', '0'))
            if desc and amt:
                lines.append(dict(desc=desc, amount=amt))
                total += amt
        execute("INSERT INTO bills (patient_id, items, total, date) VALUES (?, ?, ?, ?)",
                (patient_id, json.dumps(lines), total, datetime.datetime.now().isoformat()))
        flash("Bill generated", "success")
        return redirect(url_for('dashboard'))
    patients = query_all("SELECT patient_id, name FROM patients ORDER BY name")
    return render_template("billing.html", patients=patients)


# -------------- Utility routes ------------
@app.route('/reset-demo', methods=['POST'])
def reset_demo():
    tables = ['patients', 'doctors', 'nurses', 'medicines', 'facilities',
              'canteen_items', 'canteen_orders', 'bills']
    for t in tables:
        execute(f"DELETE FROM {t}")
    flash("Demo data cleared", "success")
    return redirect(url_for('dashboard'))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)
