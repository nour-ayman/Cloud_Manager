import subprocess
import os
import sys

def run_docker_command(command):
    """Runs a docker command and shows output in real-time"""
    try:
        # subprocess.run allows progress bars and real-time output in the terminal
        subprocess.run(command, shell=True, check=True, text=True)
    except subprocess.CalledProcessError:
        print(f"\n[ERROR] Command failed. Make sure Docker Desktop is running.")

def docker_menu():
    while True:
        print("\n" + "="*40)
        print("      DOCKER CONTAINER MANAGEMENT       ")
        print("="*40)
        print("1. Create Dockerfile")
        print("2. Build Docker Image")
        print("3. List Docker Images")
        print("4. List Running Containers")
        print("5. Stop a Container")
        print("6. Search Image (DockerHub)")
        print("7. Download/Pull Image")
        print("8. Run Container (Launch)")  # <-- Added Feature
        print("9. Back to Main Menu")        # <-- Updated Number
        print("="*40)
        
        choice = input(">> Enter your choice (1-9): ")

        if choice == '1':
            print("\n--- Create Dockerfile ---")
            path = input("Enter folder path (press Enter for current folder): ")
            if not path:
                path = "."
            
            print("Enter Dockerfile content line by line (type 'DONE' to finish):")
            content = []
            while True:
                line = input()
                if line == 'DONE':
                    break
                content.append(line)
            
            full_path = os.path.join(path, "Dockerfile")
            try:
                with open(full_path, "w") as f:
                    f.write("\n".join(content))
                print(f"[SUCCESS] Dockerfile saved at {full_path}")
            except Exception as e:
                print(f"[ERROR] Could not save file: {e}")

        elif choice == '2':
            path = input("Enter directory of Dockerfile (usually .): ")
            tag = input("Enter image name:tag (e.g., myapp:v1): ")
            run_docker_command(f"docker build -t {tag} {path}")

        elif choice == '3':
            run_docker_command("docker images")

        elif choice == '4':
            run_docker_command("docker ps -a")

        elif choice == '5':
            cid = input("Enter Container ID to stop: ")
            run_docker_command(f"docker stop {cid}")

        elif choice == '6':
            term = input("Enter image name to search: ")
            run_docker_command(f"docker search {term}")

        elif choice == '7':
            img = input("Enter image name to download (e.g., nginx): ")
            print(f"Downloading {img}... (This might take time)")
            run_docker_command(f"docker pull {img}")

        elif choice == '8':
            print("\n--- Run Container ---")
            img = input("Enter image name to run (e.g., test:1.0): ")
            name = input("Enter a name for this container (optional): ")
            
            # -d runs it in the background so the CLI doesn't hang
            if name:
                run_docker_command(f"docker run -d --name {name} {img}")
            else:
                run_docker_command(f"docker run -d {img}")
            print(f"[INFO] Container launch command sent for {img}")

        elif choice == '9':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    docker_menu()