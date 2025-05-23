# === app_frame.py ===
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from ttkbootstrap import Frame, Label, Button, Text, Scrollbar, Radiobutton
from ttkbootstrap.constants import *
from controller import (
    stage_file,
    set_project_directory,
    get_project_directory,
    run_project_entry,
    open_static_web_page,
    revert_file,
    accept_file,
    accept_batch,
    revert_batch
)

class AppFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.last_batch = []
        self.launch_type = tk.StringVar(value="python")

        self.project_dir_label = Label(self, text="📁 No project directory set", anchor="w")
        self.project_dir_label.pack(fill=X, pady=(0, 10))

        top_button_frame = Frame(self)
        top_button_frame.pack(fill=X, pady=(0, 10))

        self.set_project_btn = Button(top_button_frame, text="Set Project Directory", command=self.select_project_directory)
        self.set_project_btn.pack(side=LEFT, padx=(0, 10))

        self.select_button = Button(top_button_frame, text="Select File(s) to Test", command=self.select_files)
        self.select_button.pack(side=LEFT)

        launch_mode_frame = Frame(self)
        launch_mode_frame.pack(fill=X, pady=(0, 10))
        Label(launch_mode_frame, text="Launch Type:").pack(side=LEFT)
        Radiobutton(launch_mode_frame, text="Python App", variable=self.launch_type, value="python").pack(side=LEFT, padx=(5, 10))
        Radiobutton(launch_mode_frame, text="Static Web Page", variable=self.launch_type, value="web").pack(side=LEFT)

        self.file_label = Label(self, text="No files selected", anchor="w")
        self.file_label.pack(fill=X, pady=(0, 10))

        button_frame = Frame(self)
        button_frame.pack(fill=X, pady=(0, 10))

        self.run_button = Button(button_frame, text="Run Test", bootstyle="primary", command=self.run_test)
        self.run_button.pack(side=LEFT, padx=5)

        self.revert_button = Button(button_frame, text="Revert Batch", bootstyle="warning", command=self.revert_test_batch)
        self.revert_button.pack(side=LEFT, padx=5)

        self.accept_button = Button(button_frame, text="Accept Batch", bootstyle="success", command=self.accept_test_batch)
        self.accept_button.pack(side=LEFT, padx=5)

        self.clear_console_button = Button(button_frame, text="Clear Console", bootstyle="secondary", command=self.clear_console)
        self.clear_console_button.pack(side=LEFT, padx=5)

        output_label = Label(self, text="Console Output:")
        output_label.pack(anchor="w")

        console_frame = Frame(self)
        console_frame.pack(fill=BOTH, expand=YES)

        self.console_text = Text(console_frame, wrap="word", height=20)
        self.console_text.pack(side=LEFT, fill=BOTH, expand=YES)

        scrollbar = Scrollbar(console_frame, command=self.console_text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.console_text.config(yscrollcommand=scrollbar.set)

    def select_project_directory(self):
        directory = filedialog.askdirectory(title="Select Target Project Directory")
        if directory:
            resolved = set_project_directory(directory)
            self.project_dir_label.config(text=f"📁 Working on: {resolved}")
            self._write_console(f"Set project directory to: {resolved}")

    def select_files(self):
        file_paths = filedialog.askopenfilenames(title="Select Test File(s)")
        if not file_paths:
            self._write_console("No files selected.")
            return

        self.last_batch = []
        self.file_label.config(text=f"Selected: {len(file_paths)} files")

        for path in file_paths:
            filename = os.path.basename(path)
            project_dir = get_project_directory()

            response = messagebox.askyesnocancel("Test File Action", f"Do you want to replace an existing file with {filename}?\n\nYes = Select file to replace\nNo = Add {filename} as new\nCancel = Skip")

            if response is None:
                self._write_console(f"Skipped: {filename}")
                continue
            elif response:
                target_file_path = filedialog.askopenfilename(title=f"Choose file in project to replace with {filename}", initialdir=project_dir)
                if not target_file_path:
                    self._write_console(f"Skipped: {filename}")
                    continue
                target_filename = os.path.relpath(target_file_path, project_dir)
            else:
                dir_path = filedialog.askdirectory(title=f"Select folder to add {filename} in", initialdir=project_dir)
                if not dir_path:
                    self._write_console(f"Skipped: {filename}")
                    continue
                target_filename = os.path.relpath(os.path.join(dir_path, filename), project_dir)

            success, message = stage_file(path, target_filename)
            self._write_console(message)
            if success:
                self.last_batch.append((path, target_filename))

    def run_test(self):
        mode = self.launch_type.get()
        if mode == "python":
            success, message = run_project_entry()
        elif mode == "web":
            success, message = open_static_web_page()
        else:
            success, message = False, "Unknown launch type selected."

        self._write_console(message)

    def revert_test_batch(self):
        if not self.last_batch:
            self._write_console("No test batch to revert.")
            return
        results = revert_batch(self.last_batch)
        for (_, msg) in results:
            self._write_console(msg)

    def accept_test_batch(self):
        if not self.last_batch:
            self._write_console("No test batch to accept.")
            return
        results = accept_batch(self.last_batch)
        for (_, msg) in results:
            self._write_console(msg)

    def _write_console(self, text):
        self.console_text.config(state="normal")
        self.console_text.insert("end", text + "\n")
        self.console_text.see("end")
        self.console_text.config(state="disabled")

    def clear_console(self):
        self.console_text.config(state="normal")
        self.console_text.delete("1.0", "end")
        self.console_text.config(state="disabled")
