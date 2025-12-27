import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import sys
import os

# --- PATH CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ISO_DIR = os.path.join(DATA_DIR, "iso")
DISK_DIR = os.path.join(DATA_DIR, "disks")

os.makedirs(DISK_DIR, exist_ok=True)
os.makedirs(ISO_DIR, exist_ok=True)

# --- COLORS & FONTS ---
COLOR_BG_MAIN = "#121212"
COLOR_BG_SIDEBAR = "#1F1F1F"
COLOR_ACCENT = "#BB86FC"
COLOR_TEXT_MAIN = "#FFFFFF"
COLOR_TEXT_DIM = "#B3B3B3"
COLOR_BTN_HOVER = "#333333"

FONT_HEADER = ("Segoe UI", 24, "bold")
FONT_SUBHEADER = ("Segoe UI", 16)
FONT_BODY = ("Segoe UI", 10)

# --- CUSTOM WIDGET: ROUNDED BUTTON ---
# Standard Tkinter doesn't have radius, so we draw a custom shape!
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, width=200, height=40, radius=20, bg_color=COLOR_ACCENT, fg_color="black"):
        super().__init__(parent, width=width, height=height, bg=COLOR_BG_MAIN, highlightthickness=0)
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        
        # Draw the rounded shape (smooth polygon)
        self.rect = self.create_rounded_rect(2, 2, width-2, height-2, radius, fill=bg_color, outline=bg_color)
        self.text = self.create_text(width/2, height/2, text=text, fill=fg_color, font=("Segoe UI", 10, "bold"))
        
        # Bind events
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = (x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1)
        return self.create_polygon(points, **kwargs, smooth=True)

    def on_click(self, event):
        if self.command: self.command()
    
    def on_hover(self, event):
        self.itemconfig(self.rect, fill="white") # Hover color
        
    def on_leave(self, event):
        self.itemconfig(self.rect, fill=self.bg_color)

# --- BACKEND LOGIC ---

def log_output(message):
    if 'log_area' in globals() and log_area.winfo_exists():
        log_area.config(state='normal')
        log_area.insert(tk.END, message + "\n")
        log_area.see(tk.END)
        log_area.config(state='disabled')

def run_command_threaded(command):
    def task():
        try:
            log_output(f"> {command}")
            shell_cmd = command
            if os.name == 'nt' and 'wsl' in command:
                 shell_cmd = f'C:\\Windows\\System32\\wsl.exe {command.replace("wsl ", "")}'
            
            process = subprocess.Popen(shell_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            if stdout: log_output(stdout)
            if stderr: log_output(f"ERR: {stderr}")
            log_output("--- Done ---")
        except Exception as e:
            log_output(f"Error: {e}")
    threading.Thread(target=task, daemon=True).start()

def start_vm():
    iso_input = iso_entry.get()
    final_iso_path = ""
    if os.path.exists(iso_input):
        final_iso_path = iso_input
    elif os.path.exists(os.path.join(ISO_DIR, iso_input)):
        final_iso_path = os.path.join(ISO_DIR, iso_input)
    else:
        messagebox.showerror("Error", f"ISO not found!\nChecked: {iso_input}\nAnd: {os.path.join(ISO_DIR, iso_input)}")
        return

    disk_path = os.path.join(DISK_DIR, "vm_disk.img")
    vm_status_var.set("1 (Running)")
    log_output(f"ISO Found: {final_iso_path}")

    if not os.path.exists(disk_path):
        cmd_disk = f'qemu-img create -f qcow2 "{disk_path}" {disk_entry.get()}'
        try:
            subprocess.run(cmd_disk, shell=True, check=True)
            log_output("Disk created.")
        except Exception as e:
            log_output(f"Disk Error: {e}")
            vm_status_var.set("0 (Error)")
            return
    
    def run_vm_and_watch():
        cmd_boot = (
            f'qemu-system-x86_64 -accel whpx,kernel-irqchip=off '
            f'-m {ram_entry.get()} -smp {cpu_entry.get()} '
            f'-hda "{disk_path}" -boot d -cdrom "{final_iso_path}"'
        )
        try:
            log_output("> Launching QEMU...")
            process = subprocess.Popen(cmd_boot, shell=True)
            process.wait() 
            log_output("VM Session Ended.")
            vm_status_var.set("0 (Stopped)")
        except Exception as e:
            log_output(f"VM Error: {e}")
            vm_status_var.set("0 (Error)")

    threading.Thread(target=run_vm_and_watch, daemon=True).start()

def docker_action(action_type):
    if action_type == "pull":
        if not docker_input.get(): messagebox.showwarning("Input", "Type an image name"); return
        run_command_threaded(f"docker pull {docker_input.get()}")
    elif action_type == "stop":
        if not docker_stop_input.get(): messagebox.showwarning("Input", "Type Container ID"); return
        run_command_threaded(f"docker stop {docker_stop_input.get()}")
    elif action_type == "search":
        if not docker_search_input.get(): messagebox.showwarning("Input", "Type search term"); return
        run_command_threaded(f"docker search {docker_search_input.get()}")
    else:
        cmds = {"version": "docker --version", "ps": "docker ps -a", "images": "docker images"}
        if action_type in cmds: run_command_threaded(cmds[action_type])

# --- GUI HELPERS ---

def switch_frame(frame_to_show, btn_reference):
    frame_home.pack_forget()
    frame_vm.pack_forget()
    frame_docker.pack_forget()
    frame_to_show.pack(fill="both", expand=True, padx=20, pady=20)
    for btn in sidebar_buttons:
        btn.config(bg=COLOR_BG_SIDEBAR, fg=COLOR_TEXT_DIM, relief="flat")
    if btn_reference:
        btn_reference.config(fg=COLOR_ACCENT)

def create_nav_btn(parent, text, command):
    btn = tk.Button(parent, text=text, command=command, font=("Segoe UI", 12, "bold"),
                    bg=COLOR_BG_SIDEBAR, fg=COLOR_TEXT_DIM, activebackground=COLOR_BTN_HOVER, 
                    activeforeground=COLOR_TEXT_MAIN, bd=0, relief="flat", anchor="w", padx=20, pady=10, cursor="hand2")
    btn.pack(fill="x", pady=2)
    sidebar_buttons.append(btn)
    return btn

def create_input_row(parent, label_text, default_val):
    frame = tk.Frame(parent, bg=COLOR_BG_MAIN)
    frame.pack(fill="x", pady=5)
    lbl = tk.Label(frame, text=label_text, font=FONT_BODY, bg=COLOR_BG_MAIN, fg=COLOR_TEXT_DIM, width=15, anchor="w")
    lbl.pack(side="left")
    entry = tk.Entry(frame, font=FONT_BODY, bg="#2C2C2C", fg="white", insertbackground="white", relief="flat", bd=5)
    entry.insert(0, default_val)
    entry.pack(side="left", fill="x", expand=True)
    return entry

# --- MAIN APP SETUP ---

root = tk.Tk()
root.title("Cloud Manager (Dashboard)")
root.geometry("950x700")
root.configure(bg=COLOR_BG_MAIN)
vm_status_var = tk.StringVar(value="0 (Stopped)")
sidebar_buttons = []

sidebar = tk.Frame(root, bg=COLOR_BG_SIDEBAR, width=200)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

main_area = tk.Frame(root, bg=COLOR_BG_MAIN)
main_area.pack(side="right", fill="both", expand=True)

lbl_brand = tk.Label(sidebar, text="☁ CLOUD\nMANAGER", font=("Segoe UI", 18, "bold"), bg=COLOR_BG_SIDEBAR, fg=COLOR_TEXT_MAIN, pady=30)
lbl_brand.pack()
btn_nav_home = create_nav_btn(sidebar, "  Home", lambda: switch_frame(frame_home, btn_nav_home))
btn_nav_vm = create_nav_btn(sidebar, "  Virtual Machines", lambda: switch_frame(frame_vm, btn_nav_vm))
btn_nav_docker = create_nav_btn(sidebar, "  Docker", lambda: switch_frame(frame_docker, btn_nav_docker))
tk.Frame(sidebar, bg="#333333", height=1).pack(fill="x", pady=20, padx=10)
btn_exit = create_nav_btn(sidebar, "  Exit System", lambda: sys.exit())

frame_home = tk.Frame(main_area, bg=COLOR_BG_MAIN)
tk.Label(frame_home, text="Welcome Back!", font=FONT_HEADER, bg=COLOR_BG_MAIN, fg=COLOR_TEXT_MAIN).pack(anchor="w")
tk.Label(frame_home, text="System Status: ONLINE", font=FONT_SUBHEADER, bg=COLOR_BG_MAIN, fg=COLOR_ACCENT).pack(anchor="w", pady=5)
stats_frame = tk.Frame(frame_home, bg=COLOR_BG_MAIN)
stats_frame.pack(fill="x", pady=30)
def create_card(parent, title, var_value):
    card = tk.Frame(parent, bg="#2C2C2C", padx=20, pady=20)
    card.pack(side="left", padx=10, fill="both", expand=True)
    tk.Label(card, text=title, font=FONT_BODY, bg="#2C2C2C", fg=COLOR_TEXT_DIM).pack(anchor="w")
    tk.Label(card, textvariable=var_value, font=("Segoe UI", 20, "bold"), bg="#2C2C2C", fg=COLOR_TEXT_MAIN).pack(anchor="w")
create_card(stats_frame, "Active VMs", vm_status_var)
create_card(stats_frame, "Containers", tk.StringVar(value="Ready"))
create_card(stats_frame, "Disk Usage", tk.StringVar(value="Healthy"))

# VM Page
frame_vm = tk.Frame(main_area, bg=COLOR_BG_MAIN)
tk.Label(frame_vm, text="Virtual Machine Manager", font=FONT_HEADER, bg=COLOR_BG_MAIN, fg=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 20))
ram_entry = create_input_row(frame_vm, "RAM Size:", "4G")
cpu_entry = create_input_row(frame_vm, "CPU Cores:", "2")
disk_entry = create_input_row(frame_vm, "Disk Size:", "20G")
iso_entry = create_input_row(frame_vm, "ISO Filename:", "ubuntu-20.04.6-desktop-amd64.iso")
# Custom Rounded Button
btn_launch_vm = RoundedButton(frame_vm, text="LAUNCH VM", command=start_vm, width=250, height=45, bg_color=COLOR_ACCENT)
btn_launch_vm.pack(pady=20, anchor="e", padx=20)

# Docker Page
frame_docker = tk.Frame(main_area, bg=COLOR_BG_MAIN)
tk.Label(frame_docker, text="Docker Management", font=FONT_HEADER, bg=COLOR_BG_MAIN, fg=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 20))

docker_input = create_input_row(frame_docker, "Pull Image Name:", "hello-world")
btn_pull = RoundedButton(frame_docker, text="PULL IMAGE", command=lambda: docker_action("pull"), width=250, height=40, bg_color=COLOR_ACCENT)
btn_pull.pack(pady=(5, 15), anchor="e", padx=20)

docker_stop_input = create_input_row(frame_docker, "Stop Container ID:", "")
btn_stop = RoundedButton(frame_docker, text="STOP CONTAINER", command=lambda: docker_action("stop"), width=250, height=40, bg_color="#CF6679")
btn_stop.pack(pady=(5, 15), anchor="e", padx=20)

docker_search_input = create_input_row(frame_docker, "Search Hub:", "")
btn_search = RoundedButton(frame_docker, text="SEARCH HUB", command=lambda: docker_action("search"), width=250, height=40, bg_color="#03DAC6")
btn_search.pack(pady=(5, 15), anchor="e", padx=20)

# Quick Tools
tools_grid = tk.Frame(frame_docker, bg=COLOR_BG_MAIN)
tools_grid.pack(fill="x", pady=10)
def create_tool_btn(parent, text, action):
    tk.Button(parent, text=text, command=lambda: docker_action(action), bg="#2C2C2C", fg="white", font=FONT_BODY, relief="flat", pady=8).pack(side="left", fill="x", expand=True, padx=5)
create_tool_btn(tools_grid, "Check Version", "version")
create_tool_btn(tools_grid, "List Containers", "ps")
create_tool_btn(tools_grid, "List Images", "images")

log_frame = tk.Frame(main_area, bg="#000000", height=150)
log_frame.pack(side="bottom", fill="x", pady=20)
log_frame.pack_propagate(False)
tk.Label(log_frame, text="TERMINAL OUTPUT", bg="#000000", fg="#444444", font=("Consolas", 8)).pack(anchor="w", padx=5)
log_area = scrolledtext.ScrolledText(log_frame, bg="#000000", fg="#00FF00", font=("Consolas", 9), relief="flat")
log_area.pack(fill="both", expand=True)

switch_frame(frame_home, btn_nav_home)
root.mainloop()