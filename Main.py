import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox
import winreg


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UXPLAY_DIR = os.path.join(SCRIPT_DIR, "uxplay_bin")
UXPLAY_EXE = "uxplay-windows.exe"
APP_TITLE = "iPhone Mirror"


class MirrorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("440x300")
        self.root.configure(bg="#101418")
        self.root.resizable(False, False)
        self.process = None

        self.build_ui()
        self.check_bonjour()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def build_ui(self):
        tk.Label(
            self.root,
            text="iPhone Mirror",
            font=("Segoe UI", 18, "bold"),
            bg="#101418",
            fg="#FFFFFF",
        ).pack(pady=(24, 4))

        tk.Label(
            self.root,
            text="Mirror your iPhone screen with AirPlay",
            font=("Segoe UI", 10),
            bg="#101418",
            fg="#AEB7C2",
        ).pack(pady=(0, 18))

        self.status_label = tk.Label(
            self.root,
            text="Status: Ready",
            font=("Segoe UI", 11, "bold"),
            bg="#1B222A",
            fg="#AEB7C2",
            width=38,
            pady=10,
        )
        self.status_label.pack(padx=28, pady=5)

        self.bonjour_label = tk.Label(
            self.root,
            text="Checking Bonjour...",
            font=("Segoe UI", 10),
            bg="#101418",
            fg="#AEB7C2",
        )
        self.bonjour_label.pack(pady=(8, 12))

        self.action_button = tk.Button(
            self.root,
            text="Start Mirroring",
            command=self.toggle_mirroring,
            font=("Segoe UI", 12, "bold"),
            bg="#2E8B57",
            fg="#FFFFFF",
            activebackground="#256F46",
            activeforeground="#FFFFFF",
            bd=0,
            width=26,
            height=2,
        )
        self.action_button.pack()

    def check_bonjour(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Services\Bonjour Service",
            )
            winreg.CloseKey(key)
            self.bonjour_label.config(text="Bonjour: Available", fg="#5CCB7A")
        except (FileNotFoundError, PermissionError, WindowsError):
            self.bonjour_label.config(text="Bonjour: Not found", fg="#FF8A80")

    def get_uxplay_path(self):
        for root, _, files in os.walk(UXPLAY_DIR):
            if UXPLAY_EXE in files:
                return os.path.join(root, UXPLAY_EXE)
        return None

    def toggle_mirroring(self):
        if self.process is not None:
            self.stop_mirroring()
        else:
            self.start_mirroring()

    def start_mirroring(self):
        uxplay_path = self.get_uxplay_path()
        if not uxplay_path:
            self.set_status("UxPlay is missing", "#FF8A80")
            messagebox.showerror(
                "UxPlay is missing",
                "Place uxplay-windows.exe in the uxplay_bin folder and try again.",
            )
            return

        try:
            self.set_status("Starting AirPlay server...", "#FFD166")
            self.process = subprocess.Popen(
                [uxplay_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
            self.action_button.config(
                text="Stop Mirroring", bg="#C94C4C", activebackground="#A83D3D"
            )
            self.set_status("Ready. Select this PC on your iPhone", "#5CCB7A")
            threading.Thread(target=self.monitor_process, daemon=True).start()
        except Exception as error:
            self.process = None
            self.set_status("Could not start server", "#FF8A80")
            messagebox.showerror("Start error", str(error))

    def stop_mirroring(self):
        if self.process is not None:
            self.process.terminate()
            self.process = None
        self.action_button.config(
            text="Start Mirroring", bg="#2E8B57", activebackground="#256F46"
        )
        self.set_status("Ready", "#AEB7C2")

    def monitor_process(self):
        process = self.process
        if process is not None:
            process.wait()
            self.root.after(0, self.on_process_ended)

    def on_process_ended(self):
        if self.process is not None:
            self.process = None
            self.action_button.config(
                text="Start Mirroring", bg="#2E8B57", activebackground="#256F46"
            )
            self.set_status("Connection ended", "#FF8A80")

    def set_status(self, text, color):
        self.status_label.config(text=f"Status: {text}", fg=color)

    def on_closing(self):
        self.stop_mirroring()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    MirrorApp(root)
    root.mainloop()
