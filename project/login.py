import sqlite3
import hashlib


def employee_login():
    print("\n--- Employee Login ---")

    employee_id = input("Employee ID: ")
    password = input("Password: ")

    password_hash = hashlib.sha256(password.encode()).hexdigest()

    connection = sqlite3.connect("project/smartgov.db")
    cursor = connection.cursor()

    cursor.execute("""
    SELECT employee_id, employee_name, role
    FROM employees
    WHERE employee_id = ? AND password = ?
    """, (employee_id, password_hash))

    employee = cursor.fetchone()

    connection.close()

    if employee:
        print("\nLogin successful!")
        print("Welcome,", employee[1])
        print("Role:", employee[2])
        return True
    else:
        print("\nInvalid Employee ID or Password.")
        return False