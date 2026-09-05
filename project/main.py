import sqlite3
from citizen import submit_application
from employee import employee_dashboard
from login import employee_login
def get_next_application_id():
    connection = sqlite3.connect("project/smartgov.db")
    cursor = connection.cursor()

    cursor.execute("""
    SELECT application_id
    FROM applications
    ORDER BY application_id DESC
    LIMIT 1
    """)

    result = cursor.fetchone()

    connection.close()

    if result is None:
        return "SG-1000"

    last_number = int(result[0].split("-")[1])
    next_number = last_number + 1

    return "SG-" + str(next_number)
print("================================")
print("      SmartGov Platform")
print("================================")

print("1. Citizen")
print("2. Employe")
print("3. Track Application")
print("4. Edit Application")
print("5. Exit")

choice = input("Choose an option: ")

if choice == "1":
    submit_application()

    
elif choice == "2":
    if employee_login():
        employee_dashboard()

elif choice == "3":
    search_id = input("Enter Application ID: ")

    connection = sqlite3.connect("project/smartgov.db")
    cursor = connection.cursor()

    cursor.execute("""
    SELECT application_id, applicant_name, certificate_type,
           location, mobile, status
    FROM applications
    WHERE application_id = ?
    """, (search_id,))

    application = cursor.fetchone()

    connection.close()

    if application:
        print("\n--- Application Found ---")
        print("Application ID:", application[0])
        print("Applicant Name:", application[1])
        print("Certificate:", application[2])
        print("Location:", application[3])
        print("Mobile:", application[4])
        print("Status:", application[5])
    else:
        print("\nApplication not found.")

elif choice == "4":
    edit_id = input("Enter Application ID to edit: ")

    connection = sqlite3.connect("project/smartgov.db")
    cursor = connection.cursor()

    cursor.execute("""
    SELECT application_id, applicant_name, certificate_type, location, mobile
    FROM applications
    WHERE application_id = ?
    """, (edit_id,))

    application = cursor.fetchone()

    if application:
        print("\n--- Current Details ---")
        print("Applicant Name:", application[1])
        print("Certificate:", application[2])
        print("Location:", application[3])
        print("Mobile:", application[4])

        print("\nEnter New Details")

        new_name = input("Applicant Name: ")
        new_certificate = input("Certificate: ")
        new_location = input("Location: ")
        new_mobile = input("Mobile: ")

        cursor.execute("""
        UPDATE applications
        SET applicant_name = ?,
            certificate_type = ?,
            location = ?,
            mobile = ?
        WHERE application_id = ?
        """, (
            new_name,
            new_certificate,
            new_location,
            new_mobile,
            edit_id
        ))

        connection.commit()

        print("\nApplication details updated successfully!")

    else:
        print("\nApplication not found.")

    connection.close()

elif choice == "5":
    print("Thank you for using SmartGov Platform.")

else:
    print("Invalid choice.")