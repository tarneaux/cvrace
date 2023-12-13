# A very basic GUI which runs the plot.py and detector.py scripts in the background.

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import os
import subprocess
import shutil


class GUI:
    """
    The main GUI.
    Sections:
    1. Detector
    2. Plotter
    """

    def __init__(self, master):
        self.master = master
        self.master.title("CVRace")

        # Detector
        self.detector_frame = tk.LabelFrame(self.master, text="Detector")
        self.detector_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.detector_frame.columnconfigure(0, weight=1)
        self.detector_frame.rowconfigure(0, weight=1)

        self.detector_button = tk.Button(self.detector_frame, text="Run Detector", command=self.run_detector)
        self.detector_button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Plotter
        self.plotter_frame = tk.LabelFrame(self.master, text="Plotter")
        self.plotter_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.plotter_frame.columnconfigure(0, weight=1)
        self.plotter_frame.rowconfigure(0, weight=1)

        self.plotter_button = tk.Button(self.plotter_frame, text="Run Plotter", command=self.run_plotter)
        self.plotter_button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def run_detector(self):
        """
        Runs the detector.py script in the background.
        """
        self.detector_button.config(state="disabled")
        self.detector_process = subprocess.Popen(["./detector.py"], shell=True)
        self.detector_process.wait()
        self.detector_button.config(state="normal")
        self.save_file()

    def save_file(self):
        """
        Opens a dialog box to save the file.
        """
        self.file_name = filedialog.asksaveasfilename(initialdir="output", title="Save file", filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        if self.file_name:
            os.rename("positions.csv", self.file_name)
        else:
            os.remove("positions.csv")

    def run_plotter(self):
        """
        Runs the plot.py script in the background.
        """
        self.plotter_button.config(state="disabled")
        # Ask for the file name
        self.file_name = filedialog.askopenfilename(initialdir="output", title="Select file", filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        if not self.file_name:
            messagebox.showerror("Error", "No file selected.")
            return
        # Run the script
        shutil.copy(self.file_name, "positions.csv")
        self.plotter_process = subprocess.Popen(["./plot.py"], shell=True)
        self.plotter_process.wait()
        self.plotter_button.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()
