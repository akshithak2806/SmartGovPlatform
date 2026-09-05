import sqlite3


def employee_dashboard():
    print("\n--- Employee Dashboard ---")
    print("1. View Applications")
    print("2. Update Application Status")
    print("3. View Application History")
    print("4. Back")

    choice = input("Choose an option: ")

    # --------------------------------------------------
    # 1. VIEW ALL APPLICATIONS
    # --------------------------------------------------
    if choice == "1":
        print("\n--- Submitted Applications ---")

        connection = sqlite3.connect("project/smartgov.db")
        cursor = connection.cursor()

        cursor.execute("""
        SELECT application_id, applicant_name, certificate_type,
               location, mobile, status
        FROM applications
        ORDER BY application_id
        """)

        applications = cursor.fetchall()
        connection.close()

        if not applications:
            print("No applications found.")
        else:
            for application in applications:
                print("-----------------------------")
                print("Application ID:", application[0])
                print("Applicant Name:", application[1])
                print("Certificate:", application[2])
                print("Location:", application[3])
                print("Mobile:", application[4])
                print("Status:", application[5])

    # --------------------------------------------------
    # 2. UPDATE APPLICATION STATUS
    # --------------------------------------------------
    elif choice == "2":
        application_id = input("Enter Application ID: ")

        connection = sqlite3.connect("project/smartgov.db")
        cursor = connection.cursor()

        cursor.execute("""
        SELECT application_id, applicant_name, status
        FROM applications
        WHERE application_id = ?
        """, (application_id,))

        application = cursor.fetchone()

        if application:
            print("\nApplication Found")
            print("Application ID:", application[0])
            print("Applicant Name:", application[1])
            print("Current Status:", application[2])

            print("\nChoose New Status:")
            print("1. Under Verification")
            print("2. Approved")
            print("3. Rejected")

            status_choice = input("Choose status: ")

            if status_choice == "1":
                new_status = "Under Verification"
            elif status_choice == "2":
                new_status = "Approved"
            elif status_choice == "3":
                new_status = "Rejected"
            else:
                print("Invalid status choice.")
                connection.close()
                return

            old_status = application[2]

            cursor.execute("""
            UPDATE applications
            SET status = ?
            WHERE application_id = ?
            """, (new_status, application_id))

            cursor.execute("""
            INSERT INTO application_history
            (application_id, old_status, new_status, changed_by, changed_at)
            VALUES (?, ?, ?, ?, datetime('now'))
            """, (
                application_id,
                old_status,
                new_status,
                "EMP001",
            ))

            connection.commit()
            connection.close()

            print("\nApplication status updated successfully!")
            print("Old Status:", old_status)
            print("New Status:", new_status)

        else:
            print("\nApplication not found.")
            connection.close()

    # --------------------------------------------------
    # 3. VIEW APPLICATION HISTORY
    # --------------------------------------------------
    elif choice == "3":
        application_id = input("Enter Application ID: ")

        connection = sqlite3.connect("project/smartgov.db")
        cursor = connection.cursor()

        cursor.execute("""
        SELECT old_status, new_status, changed_by, changed_at
        FROM application_history
        WHERE application_id = ?
        ORDER BY history_id
        """, (application_id,))

        history = cursor.fetchall()
        connection.close()

        if not history:
            print("\nNo history found for this application.")
        else:
            print("\n--- Application History ---")
            print("Application ID:", application_id)

            for record in history:
                print("-----------------------------")
                print("Old Status:", record[0])
                print("New Status:", record[1])
                print("Changed By:", record[2])
                print("Changed At:", record[3])

    # --------------------------------------------------
    # 4. BACK
    # --------------------------------------------------
    elif choice == "4":
        print("Returning to main menu.")

    else:
        print("Invalid choice.")