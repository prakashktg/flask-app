import tkinter as tk
from tkinter import scrolledtext
import subprocess
import webbrowser
import os
import socket
import sys

# ---------------------- Configuration ----------------------
apps = [
    {"name": "RIASEC", "file": "app.py", "port": 5001},
    # Add more apps here:
    # {"name": "QuizApp", "file": "quiz_app.py", "port": 5002},
]

processes = {}
status_labels = {}

# ---------------------- Utility Functions ----------------------
def get_app_path(relative_path):
    """Return correct path whether running as .py or .exe"""
    try:
        base_path = sys._MEIPASS  # PyInstaller temporary folder
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def log_message(msg):
    log_box.config(state='normal')
    log_box.insert(tk.END, msg + "\n")
    log_box.see(tk.END)
    log_box.config(state='disabled')

# ---------------------- App Control ----------------------
def launch_app(app):
    file_path = get_app_path(app["file"])
    folder = os.path.dirname(file_path)
    port = app["port"]

    if file_path in processes:
        log_message(f"{app['name']} is already running.")
        return

    if is_port_in_use(port):
        status_labels[file_path].config(text="⚠ Port Busy", fg="orange")
        log_message(f"Port {port} is already in use for {app['name']}.")
        return

    try:
        proc = subprocess.Popen(
            [sys.executable, file_path],
            cwd=folder,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        processes[file_path] = proc
        status_labels[file_path].config(text="✅ Running", fg="green")
        log_message(f"Launched {app['name']} on port {port}")
        webbrowser.open(f"http://127.0.0.1:{port}")
    except Exception as e:
        status_labels[file_path].config(text="❌ Error", fg="red")
        log_message(f"Error launching {app['name']}: {e}")

def stop_app(app):
    file_path = get_app_path(app["file"])
    proc = processes.get(file_path)
    if proc:
        proc.terminate()
        proc.wait()
        del processes[file_path]
        status_labels[file_path].config(text="❌ Stopped", fg="red")
        log_message(f"Stopped {app['name']}")

def stop_all():
    for app in apps:
        stop_app(app)
    log_message("All apps stopped.")

# ---------------------- Periodic Check ----------------------
def check_processes():
    for app in apps:
        file_path = get_app_path(app["file"])
        proc = processes.get(file_path)
        if proc and proc.poll() is not None:
            # Process ended unexpectedly
            del processes[file_path]
            status_labels[file_path].config(text="❌ Stopped", fg="red")
            log_message(f"{app['name']} stopped.")
    root.after(1000, check_processes)

# ---------------------- GUI Setup ----------------------
root = tk.Tk()
root.title("Flask App Launcher")
root.geometry("600x500")

tk.Label(root, text="🚀 Launch Your Flask Apps", font=("Arial", 16)).pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=10)

for app in apps:
    row = tk.Frame(frame)
    row.pack(pady=5, fill="x")

    tk.Label(row, text=app["name"], font=("Arial", 12), width=12, anchor="w").pack(side="left", padx=5)

    tk.Button(row, text="▶ Start", font=("Arial", 11),
              command=lambda a=app: launch_app(a)).pack(side="left", padx=5)

    tk.Button(row, text="⛔ Stop", font=("Arial", 11),
              command=lambda a=app: stop_app(a)).pack(side="left", padx=5)

    status = tk.Label(row, text="❌ Stopped", font=("Arial", 11), fg="red", width=12)
    status.pack(side="left", padx=10)

    status_labels[get_app_path(app["file"])] = status

tk.Button(root, text="🧹 Stop All", fg="red", font=("Arial", 12), command=stop_all).pack(pady=10)

# ---------------------- Log Box ----------------------
log_box = scrolledtext.ScrolledText(root, height=15, width=70, state='disabled', font=("Consolas", 10))
log_box.pack(pady=10)

# Start periodic process check
root.after(1000, check_processes)

# ---------------------- Close Handler ----------------------
root.protocol("WM_DELETE_WINDOW", lambda: (stop_all(), root.destroy()))
root.mainloop()
