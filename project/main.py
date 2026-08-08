print("Welcome to SmartGov Platform")
print("====================================")
print("      SmartGov Platform")
print("====================================")
print("1. Citizen")
print("2. Employee")
print("3. Exit")

choice = input("\nChoose an option: ")

if choice == "1":
    print("\n========== Citizen Menu ==========")
    print("1. Apply for Certificate")
    print("2. Track Application")
    print("3. Back")

    citizen_choice = input("\nChoose an option: ")

    if citizen_choice == "1":
        print("\nCertificate Application")

        name = input("Enter Applicant Name: ")

        print("\nApplication Submitted Successfully!")

elif choice == "2":
    print("\n========== Employee Menu ==========")
    print("1. View Applications")
    print("2. Approve Application")
    print("3. Reject Application")

elif choice == "3":
    print("\nThank you for using SmartGov Platform.")

else:
    print("\nInvalid Choice")