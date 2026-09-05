import sqlite3
import hashlib

connection = sqlite3.connect("project/smartgov.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS applications (
    application_id TEXT PRIMARY KEY,
    applicant_name TEXT,
    certificate_type TEXT,
    location TEXT,
    mobile TEXT,
    status TEXT
)
""")

connection.commit()

print("Applications table created successfully!")
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    employee_id TEXT PRIMARY KEY,
    employee_name TEXT,
    role TEXT,
    password TEXT
)
""")

connection.commit()

print("Employees table created successfully!")
password = "1234"
password_hash = hashlib.sha256(password.encode()).hexdigest()

cursor.execute("""
INSERT OR REPLACE INTO employees
(employee_id, employee_name, role, password)
VALUES (?, ?, ?, ?)
""", (
    "EMP001",
    "Test Employee",
    "Revenue Officer",
    password_hash
))

connection.commit()

print("Test employee added successfully!")

connection.commit()

print("Application history table created successfully!")
cursor.execute("""
CREATE TABLE IF NOT EXISTS application_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id TEXT,
    old_status TEXT,
    new_status TEXT,
    changed_by TEXT,
    changed_at TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS service_requests (
    request_id TEXT PRIMARY KEY,
    customer_name TEXT,
    service TEXT,
    problem TEXT,
    location TEXT,
    status TEXT
)
""")

connection.commit()

print("Service requests table created successfully!")   
connection.close()