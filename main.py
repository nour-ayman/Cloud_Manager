import sys
import os

# Import the two parts we created earlier
# NOTE: The files must be named 'vm_manager.py' and 'docker_manager.py' for this to work!
try:
    import vm_manager
    import docker_manager
except ImportError as e:
    print("CRITICAL ERROR: Could not import your modules.")
    print(f"Details: {e}")
    print("Make sure 'vm_manager.py' and 'docker_manager.py' are in the same folder as this file.")
    sys.exit(1)

def main_menu():
    while True:
        # clear the console
        os.system('cls' if os.name == 'nt' else 'clear')

        print("========================================")
        print("      CLOUD MANAGEMENT SYSTEM           ")
        print("========================================")
        print("1. Virtual Machine Management (QEMU)")
        print("2. Docker Management")
        print("3. Exit System")
        print("========================================")
        
        choice = input(">> Enter your choice (1-3): ")

        if choice == '1':
            # Redirect to the VM Manager script
            try:
                vm_manager.create_vm()
            except Exception as e:
                print(f"An error occurred in VM Manager: {e}")
            input("\nPress Enter to return to Main Menu...")

        elif choice == '2':
            # Redirect to the Docker Manager script
            try:
                docker_manager.docker_menu()
                # pass  # Placeholder lehad ma abo hemed yebny el goz' betaa docker
            except Exception as e:
                print(f"An error occurred in Docker Manager: {e}")
            # We don't need input() here because docker_menu has its own loop

        elif choice == '3':
            print("\nExiting Cloud Management System. Goodbye!")
            sys.exit(0)

        else:
            print("\n[!] Invalid selection. Please try again.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main_menu()