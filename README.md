# 🏥 Hospital Management System

**🔗 Live Demo:** [hospital-management-system-mkkr.onrender.com](https://hospital-management-system-mkkr.onrender.com)

---

The goal was to build a real-world CRUD application that models domain complexity (relationships between patients, staff, facilities, and transactions) while staying deployment-ready.

---

## ✨ Features

| Module | What it does |
|---|---|
| 👤 **Patient Management** | Register, view, and delete patient records (name, age, gender, contact, diagnosis) |
| 🩺 **Doctor Management** | Add doctors with specialization; link to nurses |
| 👩‍⚕️ **Nurse Management** | Assign nurses to doctors with shift tracking |
| 🛏️ **Bed / Facility Management** | Add beds, assign to patients, release on discharge |
| 💊 **Pharmacy** | Track medicine stock and price; deduct inventory on purchase and auto-generate bill entries |
| 🍱 **Canteen & Food Ordering** | Menu management; patients place multi-item food orders |
| 💰 **Billing System** | Generate itemized bills per patient; aggregate revenue tracking |
| 📊 **Admin Dashboard** | Live counts for patients, doctors, nurses, beds, and medicines; revenue summary; medicine stock chart |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3, Flask 3.1 |
| **Database** | SQLite (via Python's built-in `sqlite3`) |
| **Frontend** | HTML5, CSS3, Jinja2 templating |
| **Deployment** | Render (with Gunicorn as the WSGI server) |
| **Other** | pandas, JSON for order/bill serialization |

---

## 🗂️ Project Structure

```
hospital-management-system/
│
├── app.py                  # All Flask routes and DB logic (~390 lines)
├── hospital_PROJECT.py     # Standalone CLI/prototype version
├── requirements.txt        # Flask, Gunicorn, pandas
│
├── templates/              # Jinja2 HTML templates
│   ├── index.html
│   ├── dashboard.html
│   ├── patients.html
│   ├── doctors.html
│   ├── nurses.html
│   ├── facilities.html
│   ├── pharmacy.html
│   ├── canteen.html
│   └── billing.html
│
└── static/                 # CSS and static assets
```

---

## ⚙️ Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/SargamS/hospital-management-system.git
cd hospital-management-system

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Then open [http://localhost:10000](http://localhost:10000) in your browser.

The SQLite database (`hospital.db`) is created automatically on first run — no setup required.

---

## 🧠 Technical Highlights

**Relational data modeling** — The schema links nurses to doctors via foreign key, beds to patients via `patient_id`, and bills to patients with JSON-serialized line items, reflecting real hospital record-keeping patterns.

**Inventory with auto-billing** — Purchasing a medicine decrements stock and simultaneously inserts a bill record, keeping transactions consistent without a separate transaction layer.

**Dashboard aggregation** — The dashboard route runs multiple `COUNT` and `SUM` queries and passes structured data to the frontend for a live medicine stock bar chart (rendered via Chart.js).

**Zero-config persistence** — Using SQLite with `executescript` for schema initialization means the app is fully self-contained and deploys to Render with a single `gunicorn` command and no external database service.

---

## 📸 Screenshots

### Dashboard — live stats, medicine stock chart & recent patients
![Dashboard](screenshots/dashboard.png)

### Patient Management — searchable records with add/delete
![Patient Management](screenshots/patients.png)

### Billing — itemized bill form with live receipt preview
![Billing](screenshots/billing.png)

---

## 🚀 Deployment

The app is deployed on [Render](https://render.com) using Gunicorn:

```
gunicorn app:app
```

Environment variable `PORT` is respected at startup (`os.environ.get("PORT", 10000)`), making it compatible with any PaaS platform.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
