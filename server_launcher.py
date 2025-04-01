import tkinter as tk
import subprocess
import threading
import os
import shutil
import socket
import requests
from tkinter import ttk

server_running = False
mc_process = None
property_vars = {}
properties = {}

def check_and_accept_eula():
    if not os.path.exists("eula.txt"):
        subprocess.run(["java", "-Xmx1024M", "-Xms1024M", "-jar", "server.jar", "nogui"])
        with open("eula.txt", "r") as file:
            content = file.read()
        content = content.replace("eula=false", "eula=true")
        with open("eula.txt", "w") as file:
            file.write(content)
        with open("pyserversettings.txt", "w") as settings_file:
            settings_file.write("server_initialized=true")

def start_minecraft_server():
    global server_running, mc_process
    if not os.path.exists("pyserversettings.txt"):
        with open("pyserversettings.txt", "w") as settings_file:
            settings_file.write("server_initialized=false")
    with open("pyserversettings.txt", "r") as settings_file:
        if "server_initialized=false" in settings_file.read():
            check_and_accept_eula()
    
    output_text.insert(tk.END, "Starting Minecraft Server...\n")
    mc_process = subprocess.Popen(["java", "-Xmx1024M", "-Xms1024M", "-jar", "server.jar", "nogui"], 
                                  stdin=subprocess.PIPE, 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.STDOUT, 
                                  text=True, 
                                  bufsize=1)
    threading.Thread(target=read_mc_output, daemon=True).start()
    server_running = True
    update_server_status()

def stop_minecraft_server():
    global mc_process, server_running
    if mc_process:
        mc_process.stdin.write("stop\n")
        mc_process.stdin.flush()
        mc_process = None
        output_text.insert(tk.END, "Stopping Minecraft Server...\n")
        output_text.see(tk.END)
    server_running = False
    update_server_status()

def toggle_server():
    if server_running:
        stop_minecraft_server()
    else:
        start_minecraft_server()

def update_server_status():
    if server_running:
        status_label.config(text="Server Status: Running", fg="green")
        start_stop_button.config(text="Stop Minecraft Server")
    else:
        status_label.config(text="Server Status: Stopped", fg="red")
        start_stop_button.config(text="Start Minecraft Server")

def read_mc_output():
    for line in iter(mc_process.stdout.readline, ''):
        output_text.insert(tk.END, line + "\n")
        output_text.see(tk.END)

def send_command():
    command = command_entry.get()
    if mc_process and mc_process.stdin:
        mc_process.stdin.write(command + "\n")
        mc_process.stdin.flush()
        output_text.insert(tk.END, f"> {command}\n")
        output_text.see(tk.END)
    command_entry.delete(0, tk.END)

def start_ngrok():
    output_text.insert(tk.END, "Starting NGROK Tunnel...\n")
    def run_ngrok():
        command = "ngrok tcp 25565"  # Replace with your desired command
        subprocess.Popen(["start", "cmd", "/K", f"{command} & exit"], shell=True)
    threading.Thread(target=run_ngrok, daemon=True).start()

def check_port_forwarding():
    try:
        sock = socket.create_connection(("127.0.0.1", 25565), timeout=5)
        sock.close()
        output_text.insert(tk.END, "Port 25565 is open.\n")
    except socket.error:
        output_text.insert(tk.END, "Port 25565 is not open.\n")

def backup_server():
    backup_folder = "server_backup"
    if not os.path.exists(backup_folder):
        os.mkdir(backup_folder)
    for item in os.listdir("."):
        if item not in ["server.jar", "eula.txt", "pyserversettings.txt"]:  # Exclude non-essential files
            shutil.copytree(item, os.path.join(backup_folder, item), dirs_exist_ok=True)
    output_text.insert(tk.END, f"Server files backed up to {backup_folder}.\n")

def update_server_version():
    url = "https://launcher.mojang.com/v1/objects/latest_version/server.jar"
    response = requests.get(url)
    with open("server.jar", "wb") as file:
        file.write(response.content)
    output_text.insert(tk.END, "Minecraft server updated to the latest version.\n")

def load_server_properties():
    properties.clear()
    if os.path.exists("server.properties"):
        with open("server.properties", "r") as file:
            for line in file:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    properties[key] = value
    update_properties_tab()

def update_properties_tab():
    for widget in properties_frame.winfo_children():
        widget.destroy()

    canvas = tk.Canvas(properties_frame)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(properties_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.config(command=canvas.yview)

    properties_frame_inner = tk.Frame(canvas)
    canvas.create_window((0, 0), window=properties_frame_inner, anchor="nw")

    row = 0
    for key, value in properties.items():
        tk.Label(properties_frame_inner, text=key).grid(row=row, column=0, sticky="w")
        if value.lower() in ["true", "false"]:
            var = tk.BooleanVar(value=(value.lower() == "true"))
            checkbox = tk.Checkbutton(properties_frame_inner, variable=var, onvalue=True, offvalue=False)
            checkbox.grid(row=row, column=1)
            property_vars[key] = var
        else:
            entry = tk.Entry(properties_frame_inner)
            entry.insert(0, value)
            entry.grid(row=row, column=1)
            property_vars[key] = entry
        row += 1

    properties_frame_inner.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def save_server_properties():
    with open("server.properties", "w") as file:
        for key, widget in property_vars.items():
            value = widget.get() if isinstance(widget, tk.Entry) else str(widget.get()).lower()
            file.write(f"{key}={value}\n")

def refresh_properties():
    load_server_properties()

app = tk.Tk()
app.title("Minecraft Server GUI")
app.geometry("600x500")

notebook = ttk.Notebook(app)
console_tab = ttk.Frame(notebook)
properties_tab = ttk.Frame(notebook)
notebook.add(console_tab, text="Console")
notebook.add(properties_tab, text="Server Properties")
notebook.pack(expand=True, fill="both")

status_label = tk.Label(console_tab, text="Server Status: Stopped", fg="red")
status_label.pack(pady=5)

start_stop_button = tk.Button(console_tab, text="Start Minecraft Server", command=toggle_server)
start_stop_button.pack(pady=5)

start_ngrok_button = tk.Button(console_tab, text="Start NGROK", command=start_ngrok)
start_ngrok_button.pack(pady=5)

command_entry = tk.Entry(console_tab, width=50)
command_entry.pack(pady=5)

send_command_button = tk.Button(console_tab, text="Send Command", command=send_command)
send_command_button.pack(pady=5)

output_text = tk.Text(console_tab, height=15, width=70)
output_text.pack(pady=5)

check_port_button = tk.Button(console_tab, text="Check Port Forwarding", command=check_port_forwarding)
check_port_button.pack(pady=5)

backup_button = tk.Button(console_tab, text="Backup Server Files", command=backup_server)
backup_button.pack(pady=5)

update_button = tk.Button(console_tab, text="Update Minecraft Server", command=update_server_version)
update_button.pack(pady=5)

properties_frame = tk.Frame(properties_tab)
properties_frame.pack(pady=10, padx=10, fill="both", expand=True)

load_server_properties()

save_properties_button = tk.Button(properties_tab, text="Save Properties", command=save_server_properties)
save_properties_button.pack(pady=5)

refresh_button = tk.Button(properties_tab, text="Refresh", command=refresh_properties)
refresh_button.pack(pady=5)

app.mainloop()
