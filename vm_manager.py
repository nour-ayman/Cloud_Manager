import subprocess
import json
import os
import sys

# --- CONFIGURATION PATHS ---
# We define the paths here so they are easy to change
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ISO_DIR = os.path.join(DATA_DIR, "iso")
DISK_DIR = os.path.join(DATA_DIR, "disks")
CONFIG_DIR = os.path.join(BASE_DIR, "config")

def create_vm():
    print("\n--- Create Virtual Machine (QEMU) ---")
    print("1. Enter details manually")
    print("2. Load from config file")
    print("3. Back to Main Menu")
    choice = input("Select an option (1-3): ")

    if choice == '3':
        return

    # Default Variables
    ram = "4G"
    cpu = "2"
    disk_size = "5G"
    
    # FIX: Disk is now saved in data/disks/
    disk_name = os.path.join(DISK_DIR, "vm_disk.img")
    iso_path = ""

    # Ensure directories exist
    os.makedirs(DISK_DIR, exist_ok=True)
    os.makedirs(ISO_DIR, exist_ok=True)

    # --- INPUT LOGIC ---
    if choice == '1':
        print("\nPlease enter VM Configuration:")
        ram = input(f"Enter RAM size [Default: {ram}]: ") or ram
        cpu = input(f"Enter CPU cores [Default: {cpu}]: ") or cpu
        disk_size = input(f"Enter Disk size [Default: {disk_size}]: ") or disk_size
        
        # Helper: Show available ISOs
        print(f"\nAvailable ISOs in {ISO_DIR}:")
        try:
            isos = [f for f in os.listdir(ISO_DIR) if f.endswith(".iso")]
            for f in isos: print(f" - {f}")
        except FileNotFoundError:
            print(" (No ISOs found. Please put .iso files in data/iso/)")

        iso_input = input("\nEnter ISO filename (e.g., ubuntu.iso): ").strip()
        
        # FIX: Check if user typed full path OR just filename
        if os.path.exists(iso_input):
            iso_path = iso_input
        else:
            # Try looking in the data/iso folder
            iso_path = os.path.join(ISO_DIR, iso_input)

    elif choice == '2':
        # FIX: Look in config folder first
        config_name = input("Enter config filename (e.g., vm_config.json): ")
        file_path = config_name if os.path.exists(config_name) else os.path.join(CONFIG_DIR, config_name)
        
        if not os.path.exists(file_path):
            print(f"[ERROR] Config file not found at: {file_path}")
            return
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                ram = data.get('ram', '4G')
                cpu = data.get('cpu', '2')
                disk_size = data.get('disk_size', '20G')
                # We overwrite the disk path to force organization
                disk_name = os.path.join(DISK_DIR, data.get('disk_name', 'vm_disk.img'))
                iso_path = data.get('iso_path', '')
                print(f"Loaded config: {ram} RAM, {cpu} CPU, {disk_size} Disk")
        except Exception as e:
            print(f"Error reading config: {e}")
            return
    else:
        print("Invalid choice.")
        return

    # --- CHECK ISO ---
    if not iso_path or not os.path.exists(iso_path):
        print(f"\n[ERROR] ISO file not found at: {iso_path}")
        print(f"Please move your ISO file to: {ISO_DIR}")
        return

    # --- EXECUTION LOGIC ---
    
    # Task 1: Create Hard Disk (in data/disks/)
    if not os.path.exists(disk_name):
        print(f"\n[1/2] Creating Hard Disk at {disk_name}...")
        cmd_disk = f'qemu-img create -f qcow2 "{disk_name}" {disk_size}'
        try:
            subprocess.run(cmd_disk, shell=True, check=True)
            print("Disk created successfully.")
        except subprocess.CalledProcessError:
            print("Error creating disk. Is QEMU installed?")
            return
    else:
        print(f"\n[1/2] Using existing disk: {disk_name}")

    # Task 2: Boot VM
    print(f"\n[2/2] Booting Virtual Machine...")
    
    cmd_boot = (
        f'qemu-system-x86_64 '
        f'-accel whpx,kernel-irqchip=off ' 
        f'-m {ram} '
        f'-smp {cpu} '
        f'-hda "{disk_name}" '  # Quotes added for safety
        f'-boot d '
        f'-cdrom "{iso_path}"'
    )
    
    print(f"Executing: {cmd_boot}")
    try:
        subprocess.run(cmd_boot, shell=True)
    except KeyboardInterrupt:
        print("\nVM stopped by user.")

if __name__ == "__main__":
    create_vm()