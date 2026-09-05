import sqlite3


def submit_application():
    name = input("Applicant Name: ")
    certificate = input("Certificate: ")
    location = input("Location: ")
    mobile = input("Mobile: ")

    connection = sqlite3.connect("project/smartgov.db")
    cursor = connection.cursor()

    cursor.execute("""
    SELECT application_id
    FROM applications
    ORDER BY application_id DESC
    LIMIT 1
    """)

    result = cursor.fetchone()

    if result is None:
        application_id = "SG-1000"
    else:
        last_number = int(result[0].split("-")[1])
        application_id = "SG-" + str(last_number + 1)

    cursor.execute("""
    INSERT INTO applications
    (application_id, applicant_name, certificate_type, location, mobile, status)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        application_id,
        name,
        certificate,
        location,
        mobile,
        "Submitted"
    ))

    connection.commit()
    connection.close()

    print("\nApplication Submitted Successfully!")
    print("Application ID:", application_id)
    print("Applicant Name:", name)
    print("Certificate:", certificate)
    print("Location:", location)
    print("Mobile:", mobile)
    print("Application saved to database!")