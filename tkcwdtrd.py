#!/usr/bin/env python

import tkinter as tk
from tkinter import font
from tkinter import ttk

from collections import OrderedDict
import subprocess
import os
import socket

import serial.tools.list_ports

VERSION = "1.0.0"

regfont = ("Helvetica", 18)
boldfont = ("Helvetica", 18, "bold")


class App:
    def __init__(self, root):
        self.root = root
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # swidth = self.root.winfo_screenwidth()
        # sheight = self.root.winfo_screenheight()
        # swidth -= 485
        # sheight -= 675
        swidth = sheight = 10
        self.root.geometry(
            f"650x385+{swidth}+{sheight}"
        )  # Adjust coordinates to position on screen

        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=18)
        ipaddress = self.get_local_ip()

        self.root.title(f"cwdtrd launcher {VERSION} ( on host {ipaddress} )")

        self.createwidgets()

    def createwidgets(self):
        self.entrydefs = (
            OrderedDict()
        )  # key value = [label, type (entry or combo), width, object-when-created]
        self.entrydefs["host"] = ["Host:", "entry", 25]
        self.entrydefs["port"] = ["Port:", "entry", 10]
        self.entrydefs["device"] = ["Serial Device:", "combo", 30]
        self.entrydefs["baudrate"] = ["Baud Rate:", "combo", 15]
        self.entrydefs["wpm"] = ["WPM:", "entry", 10]

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)

        row = 0
        for f in self.entrydefs:
            lbl = tk.Label(self.root, text=self.entrydefs[f][0], font=regfont)
            lbl.grid(row=row, column=0, sticky="w")

            # right now all I need is 2 types entry or combobox
            if self.entrydefs[f][1] == "entry":
                ent = tk.Entry(self.root, width=self.entrydefs[f][2], font=regfont)
                ent.grid(row=row, column=1, sticky="ew")
                self.entrydefs[f].append(ent)
            else:
                cmb = ttk.Combobox(self.root, font=regfont)
                cmb.grid(row=row, column=1, sticky="ew")
                self.entrydefs[f].append(cmb)

            self.root.rowconfigure(row, weight=1)
            row += 1

        self.entrydefs["host"][3].delete(0, tk.END)
        self.entrydefs["host"][3].insert(0, "127.0.0.1")

        self.entrydefs["port"][3].delete(0, tk.END)
        self.entrydefs["port"][3].insert(0, "9999")

        baudrates = ["4800", "9600", "19200", "38400", "115200"]
        self.entrydefs["baudrate"][3].config(values=baudrates)
        self.entrydefs["baudrate"][3].current(0)

        # Fetch all available serial/TTY ports
        rawports = serial.tools.list_ports.comports()
        devices = [p.device for p in rawports]
        self.entrydefs["device"][3].config(values=devices)
        self.entrydefs["device"][3].current(0)

        self.entrydefs["wpm"][3].delete(0, tk.END)
        self.entrydefs["wpm"][3].insert(0, "15")

        row += 3
        self.button = tk.Button(
            self.root, text="start cwdtrd", font=regfont, command=self.startdaemon
        )
        self.button.grid(row=row, column=0, pady=25, sticky="w")

        self.button1 = tk.Button(
            self.root, text="stop cwdtrd", font=regfont, command=self.stopdaemon
        )
        self.button1.grid(row=row, column=1, pady=25, sticky="w")

        row += 2
        self.lbl_status = tk.Label(self.root, text="", fg="green", font=regfont)
        self.lbl_status.grid(row=row, column=0, sticky="w")

    def get_local_ip(self):
        try:
            # Create a dummy socket to find the preferred outbound interface
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                # 8.8.8.8 is Google's public DNS, but no connection is actually made
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"

    def startdaemon(self, *args):
        # usage: cwdtrd [-h] [-s SERIALPORT] [-b BAUDRATE] [-i IPADDRESS] [-p PORT] [-w WPM] [-v]

        self.button.flash()
        host = self.entrydefs["host"][3].get()
        port = self.entrydefs["port"][3].get()
        baudrate = self.entrydefs["baudrate"][3].get()
        device = self.entrydefs["device"][3].get()
        wpm = self.entrydefs["wpm"][3].get()
        print(f"host = {host}")
        print(f"port = {port}")
        print(f"baudrate = {baudrate}")
        print(f"device = {device}")
        print(f"wpm = {wpm}")

        cmd = ["cwdtrd"]

        if host != "127.0.0.1":
            cmd.append("-i")
            cmd.append(host)
        if port != "9999":
            cmd.append("-p")
            cmd.append(port)
        if wpm != "20":
            cmd.append("-w")
            cmd.append(wpm)
        if device != "/dev/ttyUSB1":
            cmd.append("-s")
            cmd.append(device)
        if baudrate != "4800":
            cmd.append("-b")
            cmd.append(baudrate)

        print(f"doing {cmd}")

        devNULL = subprocess.DEVNULL
        kwargs = {}
        kwargs["preexec_fn"] = os.setsid

        process = subprocess.Popen(
            cmd, stdin=devNULL, stdout=devNULL, stderr=devNULL, **kwargs
        )
        print(process.pid)

        self.lbl_status.config(text="cwdtrd has started")
        self.root.after(5000, self.close_window)

    def stopdaemon(self, *args):
        self.button1.flash()
        cmd = ["stopcwdtrd"]
        print(f"doing {cmd}")
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        self.lbl_status.config(text="cwdtrd has been stopped")
        self.root.after(5000, self.close_window)

    def close_window(self):
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\ntkcwdtrd.py is terminated.")
