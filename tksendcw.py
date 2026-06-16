#!/usr/bin/env python

import tkinter as tk
from tkinter import font
from tkinter import ttk

import subprocess
import os

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
            f"1490x1150+{swidth}+{sheight}"
        )  # Adjust coordinates to position on screen

        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=18)

        self.root.title(f"SendCW to cwdtrd {VERSION}")

        self.createwidgets()

        self.root.bind("<Return>", self.Send)

    def createwidgets(self):
        topframe = tk.Frame(self.root, bg="lightblue")
        topframe.pack(fill="x", side="top", pady=20)

        lbl_host = tk.Label(topframe, text="Host:", bg="lightblue")
        lbl_host.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.ent_host = tk.Entry(topframe, width=25, font=regfont)
        self.ent_host.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.ent_host.delete(0, tk.END)
        self.ent_host.insert(0, "127.0.0.1")

        lbl_port = tk.Label(topframe, text="Port:", bg="lightblue")
        lbl_port.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.ent_port = tk.Entry(topframe, width=20, font=regfont)
        self.ent_port.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.ent_port.delete(0, tk.END)
        self.ent_port.insert(0, "4532")

        lbl_cs = tk.Label(topframe, text="Callsign:", bg="lightblue")
        lbl_cs.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.ent_callsign = tk.Entry(topframe, width=15, font=regfont)
        self.ent_callsign.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.ent_callsign.bind("<FocusOut>", self.savecallsign)
        self.readcallsign()

        lbl_evt = tk.Label(topframe, text="Event-type:", bg="lightblue")
        lbl_evt.grid(row=2, column=2, padx=5, pady=5, sticky="w")

        self.ent_eventtype = tk.Entry(topframe, width=20, font=regfont)
        self.ent_eventtype.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

        self.ent_eventtype.delete(0, tk.END)
        self.ent_eventtype.insert(0, "pota")

        lbl_ref = tk.Label(topframe, text="Reference:", bg="lightblue")
        lbl_ref.grid(row=2, column=4, padx=5, pady=5, sticky="w")

        self.ent_ref = tk.Entry(topframe, width=20, font=regfont)
        self.ent_ref.grid(row=2, column=5, padx=5, pady=5, sticky="ew")

        self.btn_cq = tk.Button(
            topframe,
            text="send cq",
            font=regfont,
            bg="blue",
            fg="white",
            activebackground="red",
            command=self.sendcq,
        )
        self.btn_cq.grid(row=4, column=2, padx=5, pady=5, sticky="w")

        self.btn_qrz = tk.Button(
            topframe,
            text="send qrz",
            font=regfont,
            bg="blue",
            fg="white",
            activebackground="red",
            command=self.sendqrz,
        )
        self.btn_qrz.grid(row=4, column=3, padx=5, pady=5, sticky="w")

        # Configure columns with equal weights so they distribute space evenly
        topframe.columnconfigure(0, weight=1)
        topframe.columnconfigure(1, weight=1)
        topframe.columnconfigure(2, weight=1)
        topframe.columnconfigure(3, weight=1)
        topframe.columnconfigure(4, weight=1)
        topframe.columnconfigure(5, weight=1)
        topframe.columnconfigure(6, weight=1)
        topframe.columnconfigure(7, weight=1)
        topframe.rowconfigure(0, weight=1)
        topframe.rowconfigure(1, weight=1)
        topframe.rowconfigure(2, weight=1)
        topframe.rowconfigure(3, weight=1)
        topframe.rowconfigure(4, weight=1)

        mainframe = tk.Frame(self.root)
        mainframe.pack(fill="both", side="top")

        lbl_cwstring = tk.Label(mainframe, text="CW String:")
        lbl_cwstring.pack(pady=(20, 5))

        self.ent_cwstring = tk.Entry(
            mainframe, width=80, font=(regfont), bg="lightgreen"
        )
        self.ent_cwstring.pack(pady=10)

        self.button = tk.Button(
            mainframe,
            text="send",
            font=regfont,
            bg="blue",
            fg="white",
            activebackground="red",
            command=self.Send,
        )
        self.button.pack(pady=25)

        lbl_history = tk.Label(mainframe, text="History:")
        lbl_history.pack(pady=(20, 5))

        self.text_history = tk.Text(
            mainframe, width=100, height=25, font=regfont, bg="lightgray"
        )
        self.text_history.pack(pady=10)
        self.text_history.config(state="normal")
        self.text_history.bind("<Double-1>", self.on_line_double_click)
        self.text_history.bind("<Key>", lambda event: "break")
        self.text_history.bind("<Enter>", self.on_hover_enter)
        self.text_history.bind("<Leave>", self.on_hover_leave)

        self.root.bind("<Control-r>", self.appendref)
        self.ent_cwstring.focus_set()

    def on_line_double_click(self, event):
        """Callback function triggered when a line is double-clicked."""
        # 1. Get the text widget that triggered the event
        text_widget = event.widget

        # 2. Find the current text index closest to the mouse click
        click_index = text_widget.index(f"@{event.x},{event.y}")

        # 3. Extract the line number from the index string (format is "line.char")
        line_number = click_index.split(".")[0]

        # 4. Define the boundaries of the full line
        line_start = f"{line_number}.0"
        line_end = f"{line_number}.end"

        # 5. Extract the text string between the boundaries
        line_text = text_widget.get(line_start, line_end)

        # Action: Print the result to the console
        # print(f"Double-clicked Line {line_number}: '{line_text}'")
        self.ent_cwstring.insert(0, line_text)

        # 6. Highlight the whole line visually (optional)
        text_widget.tag_remove("sel", "1.0", "end")  # Clear existing selection
        text_widget.tag_add("sel", line_start, line_end)  # Select the line

        self.ent_cwstring.focus_set()

        # 7. Prevents the default word-selection behavior
        return "break"

    def on_hover_enter(self, event):
        # Check if the widget state is 'disabled'
        if event.widget.cget("state") == "disabled":
            # Change pointer to a circle/no-entry sign (or 'arrow', 'pirate', etc.)
            event.widget.config(cursor="arrow")

    def on_hover_leave(self, event):
        # Restore the default text cursor ('xterm' or empty string '')
        event.widget.config(cursor="")

    def sendcq(self, *args):
        callsign = self.ent_callsign.get()
        event = self.ent_eventtype.get()
        reference = self.ent_ref.get()
        string = f"cq {event} {reference} de {callsign} {callsign} k"
        self.ent_cwstring.delete(0, tk.END)
        self.ent_cwstring.insert(0, string)
        self.Send()

    def sendqrz(self, *args):
        callsign = self.ent_callsign.get()
        string = f"{callsign} qrz? k"
        self.ent_cwstring.delete(0, tk.END)
        self.ent_cwstring.insert(0, string)
        self.Send()

    def appendref(self, *args):
        reference = self.ent_ref.get()
        ref = f" {reference} "
        print(f"insert {ref}")
        self.ent_cwstring.insert(tk.END, ref)

    def Send(self, *args):
        # get the string in the ent_cwstring
        # add it to the text_history at the top
        # send the string

        self.button.flash()

        cwstring = self.ent_cwstring.get()
        self.ent_cwstring.delete(0, tk.END)

        if cwstring:
            # self.text_history.config(state="normal")
            self.text_history.insert("1.0", f"{cwstring}\n")
            # self.text_history.config(state="readonly")

            host = self.ent_host.get()
            port = self.ent_port.get()

            cmd = ["sendcw"]

            if host != "127.0.0.1":
                cmd.append("-h")
                cmd.append(host)
            if port != "4532":
                cmd.append("-p")
                cmd.append(port)

            cmd.append(f"{cwstring}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            print(result.stdout.strip())

        self.ent_cwstring.focus_set()
        # subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def readcallsign(self):
        filename = os.environ["HOME"] + "/sendcw.callsign.txt"
        try:
            with open(filename, "r") as file:
                callsign = file.read().strip()
                self.ent_callsign.delete(0, tk.END)
                self.ent_callsign.insert(0, callsign)
        except FileNotFoundError:
            callsign = ""
            self.ent_callsign.delete(0, tk.END)
            self.ent_callsign.insert(0, callsign)

    def savecallsign(self, *args):
        filename = os.environ["HOME"] + "/sendcw.callsign.txt"
        with open(filename, "w") as file:
            callsign = self.ent_callsign.get()
            file.write(f"{callsign}\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\ntksendcw.py is terminated.")
