import tkinter as tk
import requests
import socket
import platform


def get_external_ip():
    try:
        response = requests.get('https://api.ipify.org')
        return response.text
    except requests.RequestException:
        return "Unable to get external IP"


def get_local_ip():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except socket.error:
        return "Unable to get local IP"


def get_system_info():
    system = platform.system()
    node = platform.node()
    release = platform.release()
    version = platform.version()
    machine = platform.machine()
    processor = platform.processor()

    return {
        "System": system,
        "Node": node,
        "Release": release,
        "Version": version,
        "Machine": machine,
        "Processor": processor
    }


def display_info():
    external_ip = get_external_ip()
    local_ip = get_local_ip()
    system_info = get_system_info()

    info = f"External IP: {external_ip}\n"
    info += f"Local IP: {local_ip}\n"
    info += "System Information:\n"
    for key, value in system_info.items():
        info += f"{key}: {value}\n"

    root = tk.Tk()
    root.title("System Information")

    text = tk.Text(root, height=15, width=50)
    text.pack()
    text.insert(tk.END, info)

    root.mainloop()


if __name__ == "__main__":
    display_info()
