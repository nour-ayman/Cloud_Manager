# ☁️ Cloud Manager (v2.1)

A powerful, GUI-based dashboard for managing Virtual Machines (QEMU) and Docker Containers locally. Built for speed, modularity, and ease of use.

## Version History
* **v1.0 (Local Prototype):** Initial Command-Line (CLI) version focused on core QEMU logic.
* **v2.0 (Beta):** Introduction of the Dark-Mode GUI and basic Docker integration (Pull/Stop).
* **v2.1 (Current - Enhanced):** Major UI overhaul and full container lifecycle support. Added Sidebar Tooling and "Run Container" functionality.

##  New in v2.1
* **Container Execution:** Added "Run Container" (Launch) feature in both GUI and CLI.
* **Optimized Sidebar UI:** Moved system utilities (Version check, List Containers/Images, Dockerfile Creator) to a vertical sidebar for instant access across all pages.
* **Smart Process Management:** Updated container listing to `ps -a` to help track exited or crashed processes.
* **Performance Fixes:** Optimized Dockerfile build context with `.dockerignore` to prevent massive 8GB image sizes.
* **Enhanced Terminal:** Fixed terminal output visibility to remain locked at the bottom during page transitions.

## Folder Structure
The project uses a strict structure to keep large files organized:
* `data/iso/` - **(Action Required)** Place your `.iso` files here.
* `data/disks/` - VM hard disks are generated here automatically.
* `config/` - JSON configuration files.

## Requirements
* **Python 3.x**
* **Tkinter** (Usually built-in with Python)
* **QEMU** (Must be installed and in your System PATH)
* **Docker Desktop** (Must be running)

## How to Run
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/nour-ayman/Cloud_Manager.git](https://github.com/nour-ayman/Cloud_Manager.git)
    ```
2.  **Setup ISOs:**
    Place your preferred Linux `.iso` inside `data/iso/`.
3.  **Start the Dashboard:**
    ```bash
    # Run the modern GUI
    python gui_main.py

    # Run the classic CLI
    python main.py
    ```

## Contributors
* **Nour El-Dine Ayman** - Lead Developer (GUI & VM Logic)
* **Ahmed Medhat** - Docker Backend Integration & Container Lifecycle
