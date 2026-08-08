from backend.auth import register,login
def main():
    while True:
        print("\n================================================")
        print("LOCAL FARMERS PRODUCE MARKETPLACE")
        print("\n================================================")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice=input("Enter your choice:")
        if choice=="1":
            register()
        elif choice=="2":
            login()
        elif choice=="3":
            print("Thank you for using our marketplace!")
            break
        else:
            print("Invalid choice. Please try again.")
if __name__=="__main__":
    main()