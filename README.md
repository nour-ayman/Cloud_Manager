# ☁️ Cloud Manager (v2.0 Beta)

A powerful, GUI-based dashboard for managing Virtual Machines (QEMU) and Docker Containers locally.

## Version History
* **v1.0 (Local Prototype):** Initial Command-Line (CLI) version focused on core QEMU logic. Developed and tested locally.
* **v2.0 (Current Beta):** Major update introducing a full GUI, Docker integration, and optimized folder structure. Now hosted on GitHub.

## New in v2.0
* **Graphical User Interface:** Full dark-mode dashboard with modern rounded buttons.
* **Unified Control:** Manage both QEMU VMs and Docker containers in one place.
* **Smart Docker Tools:** Search DockerHub, pull images, and stop containers with one click.
* **Automatic File Management:** Intelligently handles ISO paths and Disk creation in `data/`.

## Folder Structure
The project uses a strict structure to keep large files organized:
* `data/iso/` - **(Action Required)** Place your `.iso` files here.
* `data/disks/` - VM hard disks are generated here automatically.
* `config/` - JSON configuration files.

## Requirements
* Python 3.x
* `tkinter` (Usually built-in)
* **QEMU** (Must be in your System PATH)
* **Docker Desktop** (Must be running)

## How to Run
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/nour-ayman/Cloud_Manager.git]
    ```
2.  **Add your ISO:**
    Download an Ubuntu ISO and move it to the `data/iso/` folder.
3.  **Start the Dashboard:**
    ```bash
    GUI: python gui_main.py
    CLI: python main.py
    ```

## Contributors
* **Nour El-Dine Ayman** - Lead Developer (GUI & VM Logic)
* **Ahmed Medhat** - Docker Backend Integration