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
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, width=200, height=40, radius=20, bg_color=COLOR_ACCENT, fg_color="black"):
        super().__init__(parent, width=width, height=height, bg=COLOR_BG_MAIN, highlightthickness=0)
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        
        self.rect = self.create_rounded_rect(2, 2, width-2, height-2, radius, fill=bg_color, outline=bg_color)
        self.text = self.create_text(width/2, height/2, text=text, fill=fg_color, font=("Segoe UI", 10, "bold"))
        
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = (x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1)
        return self.create_polygon(points, **kwargs, smooth=True)

    def on_click(self, event):
        if self.command: self.command()
    
    def on_hover(self, event):
        self.itemconfig(self.rect, fill="white")
        
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

def create_dockerfile_ui():
    df_win = tk.Toplevel(root)
    df_win.title("Create Dockerfile")
    df_win.geometry("500x500")
    df_win.configure(bg=COLOR_BG_MAIN)

    tk.Label(df_win, text="Save Path (Directory):", bg=COLOR_BG_MAIN, fg=COLOR_TEXT_DIM).pack(pady=5, anchor="w", padx=10)
    path_entry = tk.Entry(df_win, bg="#2C2C2C", fg="white", relief="flat")
    path_entry.insert(0, BASE_DIR)
    path_entry.pack(fill="x", padx=10, pady=5)

    tk.Label(df_win, text="Dockerfile Content:", bg=COLOR_BG_MAIN, fg=COLOR_TEXT_DIM).pack(pady=5, anchor="w", padx=10)
    content_text = scrolledtext.ScrolledText(df_win, height=12, bg="#2C2C2C", fg="white", insertbackground="white")
    content_text.insert(tk.END, "FROM python:3.9-slim\nWORKDIR /app\nCOPY . .\nCMD [\"python\", \"main.py\"]")
    content_text.pack(fill="both", expand=True, padx=10, pady=5)

    def save_file():
        full_path = os.path.join(path_entry.get(), "Dockerfile")
        try:
            with open(full_path, "w") as f:
                f.write(content_text.get("1.0", tk.END).strip())
            messagebox.showinfo("Success", f"Dockerfile created at:\n{full_path}")
            df_win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    RoundedButton(df_win, text="SAVE FILE", command=save_file, width=150).pack(pady=20)

def start_vm():
    iso_input = iso_entry.get()
    final_iso_path = ""
    if os.path.exists(iso_input):
        final_iso_path = iso_input
    elif os.path.exists(os.path.join(ISO_DIR, iso_input)):
        final_iso_path = os.path.join(ISO_DIR, iso_input)
    else:
        messagebox.showerror("Error", f"ISO not found!")
        return

    disk_path = os.path.join(DISK_DIR, "vm_disk.img")
    vm_status_var.set("1 (Running)")
    
    if not os.path.exists(disk_path):
        cmd_disk = f'qemu-img create -f qcow2 "{disk_path}" {disk_entry.get()}'
        subprocess.run(cmd_disk, shell=True)
    
    def run_vm_and_watch():
        cmd_boot = (
            f'qemu-system-x86_64 -accel whpx,kernel-irqchip=off '
            f'-m {ram_entry.get()} -smp {cpu_entry.get()} '
            f'-hda "{disk_path}" -boot d -cdrom "{final_iso_path}"'
        )
        process = subprocess.Popen(cmd_boot, shell=True)
        process.wait() 
        vm_status_var.set("0 (Stopped)")

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
    elif action_type == "build":
        tag = docker_build_tag.get()
        if not tag: messagebox.showwarning("Input", "Enter an image tag"); return
        run_command_threaded(f"docker build -t {tag} .")
    elif action_type == "run":
        img = docker_run_img.get()
        name = docker_run_name.get()
        if not img: messagebox.showwarning("Input", "Enter an image name to run"); return
        cmd = f"docker run -d --name {name} {img}" if name else f"docker run -d {img}"
        run_command_threaded(cmd)
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
        btn.config(bg=COLOR_BG_SIDEBAR, fg=COLOR_TEXT_DIM)
    if btn_reference:
        btn_reference.config(fg=COLOR_ACCENT)

def create_nav_btn(parent, text, command):
    btn = tk.Button(parent, text=text, command=command, font=("Segoe UI", 12, "bold"),
                    bg=COLOR_BG_SIDEBAR, fg=COLOR_TEXT_DIM, activebackground=COLOR_BTN_HOVER, 
                    activeforeground=COLOR_TEXT_MAIN, bd=0, relief="flat", anchor="w", padx=20, pady=10, cursor="hand2")
    btn.pack(fill="x")
    sidebar_buttons.append(btn)
    return btn

def create_sidebar_tool(parent, text, action):
    # Specialized helper for tools at the bottom of the sidebar
    cmd = lambda: create_dockerfile_ui() if action == "create_df" else docker_action(action)
    btn = tk.Button(parent, text=text, command=cmd, font=("Segoe UI", 10),
                    bg=COLOR_BG_SIDEBAR, fg="#757575", activebackground=COLOR_BTN_HOVER, 
                    activeforeground=COLOR_ACCENT, bd=0, relief="flat", anchor="w", padx=25, pady=5, cursor="hand2")
    btn.pack(fill="x")

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
root.title("Cloud Manager Dashboard")
root.geometry("1000x800")
root.configure(bg=COLOR_BG_MAIN)
vm_status_var = tk.StringVar(value="0 (Stopped)")
sidebar_buttons = []

# 1. Sidebar
sidebar = tk.Frame(root, bg=COLOR_BG_SIDEBAR, width=220)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

# 2. Terminal (Bottom)
log_frame = tk.Frame(root, bg="#000000", height=180)
log_frame.pack(side="bottom", fill="x")
log_frame.pack_propagate(False)
tk.Label(log_frame, text="TERMINAL OUTPUT", bg="#000000", fg="#444444", font=("Consolas", 8)).pack(anchor="w", padx=5)
log_area = scrolledtext.ScrolledText(log_frame, bg="#000000", fg="#00FF00", font=("Consolas", 10), relief="flat")
log_area.pack(fill="both", expand=True)

# 3. Main Content Area (No more scrollbar needed!)
main_area = tk.Frame(root, bg=COLOR_BG_MAIN)
main_area.pack(side="right", fill="both", expand=True)

# --- SIDEBAR CONTENT ---
lbl_brand = tk.Label(sidebar, text="☁ CLOUD\nMANAGER", font=("Segoe UI", 18, "bold"), bg=COLOR_BG_SIDEBAR, fg=COLOR_TEXT_MAIN, pady=30)
lbl_brand.pack()

# Main Nav
btn_nav_home = create_nav_btn(sidebar, "  Home", lambda: switch_frame(frame_home, btn_nav_home))
btn_nav_vm = create_nav_btn(sidebar, "  Virtual Machines", lambda: switch_frame(frame_vm, btn_nav_vm))
btn_nav_docker = create_nav_btn(sidebar, "  Docker", lambda: switch_frame(frame_docker, btn_nav_docker))

# Spacer/Divider
tk.Label(sidebar, text="SYSTEM TOOLS", font=("Segoe UI", 8, "bold"), bg=COLOR_BG_SIDEBAR, fg="#444444", pady=15).pack(anchor="w", padx=20)

# The 4 Sidebar Tools (Vertically stacked)
create_sidebar_tool(sidebar, "⚙ Check Version", "version")
create_sidebar_tool(sidebar, "📦 List Containers", "ps")
create_sidebar_tool(sidebar, "🖼 List Images", "images")
create_sidebar_tool(sidebar, "📝 Create Dockerfile", "create_df")

# Exit at very bottom
tk.Frame(sidebar, bg="#333333", height=1).pack(fill="x", pady=10, padx=10)
btn_exit = create_nav_btn(sidebar, "  Exit System", lambda: sys.exit())

# --- PAGES ---
# Home Page
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
disk_entry = create_input_row(frame_vm, "Disk Size:", "5G")
iso_entry = create_input_row(frame_vm, "ISO Filename:", "ubuntu-20.04.6-desktop-amd64.iso")
btn_launch_vm = RoundedButton(frame_vm, text="LAUNCH VM", command=start_vm, width=250, height=45, bg_color=COLOR_ACCENT)
btn_launch_vm.pack(pady=20, anchor="e", padx=20)

# Docker Page (COMPACT VERSION)
frame_docker = tk.Frame(main_area, bg=COLOR_BG_MAIN)
tk.Label(frame_docker, text="Docker Management", font=FONT_HEADER, bg=COLOR_BG_MAIN, fg=COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 10))

docker_input = create_input_row(frame_docker, "Pull Image Name:", "")
btn_pull = RoundedButton(frame_docker, text="PULL IMAGE", command=lambda: docker_action("pull"), width=250, height=35, bg_color=COLOR_ACCENT)
btn_pull.pack(pady=2, anchor="e", padx=20)

docker_build_tag = create_input_row(frame_docker, "Build Image Tag:", "")
btn_build = RoundedButton(frame_docker, text="BUILD IMAGE", command=lambda: docker_action("build"), width=250, height=35, bg_color="#BB86FC")
btn_build.pack(pady=2, anchor="e", padx=20)

docker_run_img = create_input_row(frame_docker, "Run Image Name:", "")
docker_run_name = create_input_row(frame_docker, "Container Name:", "")
btn_run = RoundedButton(frame_docker, text="RUN CONTAINER", command=lambda: docker_action("run"), width=250, height=35, bg_color="#03DAC6")
btn_run.pack(pady=2, anchor="e", padx=20)

docker_stop_input = create_input_row(frame_docker, "Stop Container ID:", "")
btn_stop = RoundedButton(frame_docker, text="STOP CONTAINER", command=lambda: docker_action("stop"), width=250, height=35, bg_color="#CF6679")
btn_stop.pack(pady=2, anchor="e", padx=20)

docker_search_input = create_input_row(frame_docker, "Search Image:", "")
btn_search = RoundedButton(frame_docker, text="SEARCH IMAGE", command=lambda: docker_action("search"), width=250, height=35, bg_color="#03DAC6")
btn_search.pack(pady=2, anchor="e", padx=20)

switch_frame(frame_home, btn_nav_home)
root.mainloop()