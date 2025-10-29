import os
import glob
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import math
import logging

# Configure logging
LOG_FILE = os.path.join(os.path.expanduser("~"), "Documents", "fast_uploader_debug.log")
logging.basicConfig(
    level=logging.INFO, # Default to INFO, will be adjusted by debug_mode
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logging.info("Application started.")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_NAME = "fast_uploader.json"
CONFIG_DIR = os.path.join(os.path.expanduser("~"), "Documents")
CONFIG_FILE = os.path.join(CONFIG_DIR, CONFIG_FILE_NAME)
SHAREX_PATH = r"C:\Program Files\ShareX\ShareX.exe"
VIDEO_EXTENSIONS = ("*.mp4", "*.mkv", "*.mov", "*.avi", "*.wmv")

PRESET_THEMES = {
    "Default (Pink)": {
        "bg": "#FFC0CB",
        "fg": "#5D4037",
        "btn_bg": "#FF69B4",
        "btn_fg": "#FFFFFF",
        "entry_bg": "#FFF0F5",
        "tree_bg": "#FFF0F5",
        "tree_fg": "#5D4037",
        "tree_heading": "#FF69B4",
    },
    "Dark Mode": {
        "bg": "#2E2E2E",
        "fg": "#E0E0E0",
        "btn_bg": "#4CAF50",
        "btn_fg": "#FFFFFF",
        "entry_bg": "#424242",
        "tree_bg": "#424242",
        "tree_fg": "#E0E0E0",
        "tree_heading": "#4CAF50",
    },
    "Light Mode": {
        "bg": "#F0F0F0",
        "fg": "#333333",
        "btn_bg": "#2196F3",
        "btn_fg": "#FFFFFF",
        "entry_bg": "#FFFFFF",
        "tree_bg": "#FFFFFF",
        "tree_fg": "#333333",
        "tree_heading": "#2196F3",
    },
    "Ocean Blue": {
        "bg": "#B0E0E6", # Powder Blue
        "fg": "#00507F", # Dark Blue
        "btn_bg": "#4682B4", # Steel Blue
        "btn_fg": "#FFFFFF",
        "entry_bg": "#ADD8E6", # Light Blue
        "tree_bg": "#ADD8E6",
        "tree_fg": "#00507F",
        "tree_heading": "#4682B4",
    }
}


class PreferencesWindow(tk.Toplevel):
    def __init__(self, parent, data, config_file_path, apply_theme_callback, populate_recent_clips_callback):
        super().__init__(parent)
        logging.debug("PreferencesWindow: Initializing...")
        self.title("Preferences")
        self.parent = parent
        self.data = data
        self.config_file_path = config_file_path
        self.apply_theme_callback = apply_theme_callback
        self.populate_recent_clips_callback = populate_recent_clips_callback
        self.current_theme_colors = self.parent.current_theme_colors # Inherit theme from parent
        self.config(bg=self.current_theme_colors["bg"])
        self.create_widgets()
        self.apply_theme()
        logging.debug("PreferencesWindow: Initialized.")


    def apply_theme(self):
        logging.debug("PreferencesWindow: Applying theme.")
        # Update root window background
        self.config(bg=self.current_theme_colors["bg"])

        # Update ttk styles
        style = ttk.Style(self)
        style.configure("TLabel", background=self.current_theme_colors["bg"], foreground=self.current_theme_colors["fg"])
        style.configure("TFrame", background=self.current_theme_colors["bg"])
        style.configure("TLabelFrame", background=self.current_theme_colors["bg"], foreground=self.current_theme_colors["fg"])
        style.configure(
            "TButton",
            background=self.current_theme_colors["btn_bg"],
            foreground=self.current_theme_colors["btn_fg"],
            borderwidth=1,
        )
        style.map("TButton", background=[("active", self.current_theme_colors["bg"])])
        style.configure("TEntry", fieldbackground=self.current_theme_colors["entry_bg"], foreground=self.current_theme_colors["fg"])
        style.configure(
            "Treeview",
            background=self.current_theme_colors["tree_bg"],
            foreground=self.current_theme_colors["tree_fg"],
            fieldbackground=self.current_theme_colors["tree_bg"],
        )
        style.configure(
            "Treeview.Heading",
            background=self.current_theme_colors["tree_heading"],
            foreground=self.current_theme_colors["btn_fg"],
        )
        style.configure("TCombobox", fieldbackground=self.current_theme_colors["entry_bg"], foreground=self.current_theme_colors["fg"])

        for widget in self.winfo_children():
            self._update_widget_colors(widget)

        self.update_idletasks() # Update widgets to calculate their sizes
        # Set geometry to fit content and disable resizing
        self.geometry(f"{self.winfo_reqwidth()}x{self.winfo_reqheight()}")
        self.resizable(False, False)
        logging.debug("PreferencesWindow: Theme applied and window geometry set.")

    def _update_widget_colors(self, widget):
        try:
            if isinstance(widget, (tk.Label, ttk.Label)):
                widget.config(bg=self.current_theme_colors["bg"], fg=self.current_theme_colors["fg"])
            elif isinstance(widget, (tk.Frame, ttk.Frame, tk.LabelFrame, ttk.LabelFrame)):
                widget.config(bg=self.current_theme_colors["bg"], fg=self.current_theme_colors["fg"])
        except tk.TclError:
            logging.debug(f"PreferencesWindow: TclError when updating widget colors for {widget}.")
            pass
        for child in widget.winfo_children():
            self._update_widget_colors(child)


    def create_widgets(self):
        logging.debug("PreferencesWindow: Creating widgets.")
        style = ttk.Style(self)
        style.theme_use("clam")

        # ShareX Host
        host_frame = ttk.LabelFrame(self, text="💌 ShareX Host 💌")
        host_frame.pack(padx=10, pady=5, fill="x", expand=True)
        self.host_var = tk.StringVar(value=self.data.get("sharex_host", "ezhost"))
        self.host_entry = ttk.Entry(host_frame, textvariable=self.host_var)
        self.host_entry.pack(fill="x", padx=5, pady=5)
        logging.debug(f"PreferencesWindow: ShareX Host entry value: {self.host_var.get()}")

        # Toast Position
        toast_pos_frame = ttk.LabelFrame(self, text="📍 Toast Position 📍")
        toast_pos_frame.pack(padx=10, pady=5, fill="x", expand=True)
        self.toast_pos_var = tk.StringVar(value=self.data.get("toast_position", "Bottom Right"))
        self.toast_pos_combo = ttk.Combobox(
            toast_pos_frame,
            textvariable=self.toast_pos_var,
            values=["Top Left", "Top Right", "Bottom Left", "Bottom Right"],
            state="readonly",
        )
        self.toast_pos_combo.pack(fill="x", padx=5, pady=5)
        logging.debug(f"PreferencesWindow: Toast Position selected: {self.toast_pos_var.get()}")

        # Toast Duration
        toast_duration_frame = ttk.LabelFrame(self, text="⏱️ Toast Duration (s) ⏱️")
        toast_duration_frame.pack(padx=10, pady=5, fill="x", expand=True)
        self.toast_duration_var = tk.StringVar(value=self.data.get("toast_duration", "5"))
        self.toast_duration_entry = ttk.Entry(
            toast_duration_frame, textvariable=self.toast_duration_var
        )
        self.toast_duration_entry.pack(fill="x", padx=5, pady=5)
        logging.debug(f"PreferencesWindow: Toast Duration entry value: {self.toast_duration_var.get()}")

        # Number of Recent Clips
        num_clips_frame = ttk.LabelFrame(self, text="🔢 Number of Recent Clips 🔢")
        num_clips_frame.pack(padx=10, pady=5, fill="x", expand=True)
        self.num_recent_clips_var = tk.StringVar(value=self.data.get("num_recent_clips", "5"))
        self.num_recent_clips_entry = ttk.Entry(
            num_clips_frame, textvariable=self.num_recent_clips_var
        )
        self.num_recent_clips_entry.pack(fill="x", padx=5, pady=5)
        self.num_recent_clips_entry.bind("<KeyRelease>", self._on_num_recent_clips_change)
        logging.debug(f"PreferencesWindow: Number of Recent Clips entry value: {self.num_recent_clips_var.get()}")

        # Video Base Directory
        video_dir_frame = ttk.LabelFrame(self, text="📁 Video Base Directory 📁")
        video_dir_frame.pack(padx=10, pady=5, fill="x", expand=True)
        self.video_base_dir_var = tk.StringVar(value=self.data.get("video_base_dir", SCRIPT_DIR))
        video_dir_entry = ttk.Entry(video_dir_frame, textvariable=self.video_base_dir_var)
        video_dir_entry.pack(side="left", fill="x", expand=True, padx=(5, 0), pady=5)
        browse_button = ttk.Button(video_dir_frame, text="Browse", command=self.browse_video_base_dir)
        browse_button.pack(side="right", padx=(0, 5), pady=5)
        logging.debug(f"PreferencesWindow: Video Base Directory entry value: {self.video_base_dir_var.get()}")

        # Save Button
        save_button = ttk.Button(self, text="💾 Save Changes", command=self.save_preferences)
        save_button.pack(pady=10)
        logging.debug("PreferencesWindow: Save Changes button created.")

    def _on_num_recent_clips_change(self, event):
        logging.debug("PreferencesWindow: _on_num_recent_clips_change triggered (KeyRelease).")
        # This will be handled by parent's populate_recent_clips after save
        pass

    def browse_video_base_dir(self):
        logging.info("PreferencesWindow: Opening browse dialog for video base directory.")
        initial_dir = self.video_base_dir_var.get()
        if not os.path.isdir(initial_dir):
            logging.debug(f"PreferencesWindow: Initial directory '{initial_dir}' not found, falling back to home directory.")
            initial_dir = os.path.expanduser("~")
        folder_selected = filedialog.askdirectory(initial_dir=initial_dir)
        if folder_selected:
            self.video_base_dir_var.set(folder_selected)
            logging.info(f"PreferencesWindow: New video base directory selected: {folder_selected}")
        else:
            logging.info("PreferencesWindow: Video base directory selection cancelled.")

    def save_preferences(self):
        logging.info("PreferencesWindow: Saving preferences.")
        self.data["sharex_host"] = self.host_var.get()
        self.data["toast_position"] = self.toast_pos_var.get()
        self.data["toast_duration"] = self.toast_duration_var.get()

        try:
            num_clips_val = int(self.num_recent_clips_var.get())
            if num_clips_val < 1:
                num_clips_val = 1
                logging.warning(f"PreferencesWindow: Invalid num_recent_clips ({self.num_recent_clips_var.get()}), defaulting to 1.")
            self.data["num_recent_clips"] = num_clips_val
            logging.debug(f"PreferencesWindow: num_recent_clips saved as: {num_clips_val}")
        except ValueError:
            logging.error(f"PreferencesWindow: Invalid input for Number of Recent Clips: {self.num_recent_clips_var.get()}. Defaulting to 5.", exc_info=True)
            messagebox.showerror("Invalid Input", "Number of Recent Clips must be an integer. Defaulting to 5.")
            self.data["num_recent_clips"] = 5
            self.num_recent_clips_var.set("5")

        self.data["video_base_dir"] = self.video_base_dir_var.get()
        logging.debug(f"PreferencesWindow: video_base_dir saved as: {self.video_base_dir_var.get()}")

        try:
            with open(self.config_file_path, "w") as f:
                json.dump(self.data, f, indent=4)
            logging.info("PreferencesWindow: Config file updated successfully.")
        except Exception as e:
            logging.error(f"PreferencesWindow: Failed to save config file: {e}", exc_info=True)
            messagebox.showerror("Save Error", f"Failed to save preferences: {e}")

        # Trigger updates in the main ConfigGUI
        logging.debug("PreferencesWindow: Calling populate_recent_clips_callback.")
        self.populate_recent_clips_callback() # To update the recent clips display
        logging.debug("PreferencesWindow: Calling parent.populate_folder_stats.")
        self.parent.populate_folder_stats() # To update folder stats if base dir changed
        self.destroy()
        logging.info("PreferencesWindow: Window destroyed.")


class ConfigGUI(tk.Tk):
    def __init__(self, data, recent_clips=None):
        super().__init__()
        self.title("6c75 Fast Uploader Settings")
        self.geometry("800x700") # Increased default size
        self.resizable(True, True) # Ensure it's resizable
        self.data = data
        self.current_theme_name = self.data.get("theme", "Default (Pink)")
        self.current_theme_colors = PRESET_THEMES.get(self.current_theme_name, PRESET_THEMES["Default (Pink)"])
        self.config(bg=self.current_theme_colors["bg"])
        self.recent_clips = recent_clips if recent_clips is not None else []
        self.debug_mode_var = tk.BooleanVar(value=self.data.get("debug_mode", False))
        if self.debug_mode_var.get():
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.INFO)
        logging.debug(f"ConfigGUI initialized with debug_mode={self.debug_mode_var.get()}")

        self.create_menus()
        self.create_widgets()
        self.apply_theme()
        self.populate_folder_stats()
        self.populate_recent_clips()

    def create_menus(self):
        logging.debug("Creating menus...")
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Settings Menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        # Preferences Option
        settings_menu.add_command(label="Preferences...", command=self.open_preferences_window)

        # Theme submenu
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Theme", menu=theme_menu)
        for theme_name in PRESET_THEMES.keys():
            theme_menu.add_command(label=theme_name, command=lambda name=theme_name: self.set_theme(name))

        # Debug Mode Toggle
        settings_menu.add_checkbutton(label="Debug Mode", variable=self.debug_mode_var, command=self.toggle_debug_mode)
        logging.debug("Menus created.")

    def toggle_debug_mode(self):
        self.data["debug_mode"] = self.debug_mode_var.get()
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.data, f, indent=4)
        if self.debug_mode_var.get():
            logging.getLogger().setLevel(logging.DEBUG)
            logging.info("Debug mode enabled.")
        else:
            logging.getLogger().setLevel(logging.INFO)
            logging.info("Debug mode disabled.")

    def open_preferences_window(self):
        logging.debug("Opening preferences window.")
        PreferencesWindow(self, self.data, CONFIG_FILE, self.apply_theme, self.populate_recent_clips)

    def apply_theme(self):
        logging.debug(f"Applying theme: {self.current_theme_name}")
        self.config(bg=self.current_theme_colors["bg"])

        style = ttk.Style(self)
        style.configure("TLabel", background=self.current_theme_colors["bg"], foreground=self.current_theme_colors["fg"])
        style.configure("TFrame", background=self.current_theme_colors["bg"])
        style.configure("TLabelFrame", background=self.current_theme_colors["bg"], foreground=self.current_theme_colors["fg"])
        style.configure(
            "TButton",
            background=self.current_theme_colors["btn_bg"],
            foreground=self.current_theme_colors["btn_fg"],
            borderwidth=1,
        )
        style.map("TButton", background=[("active", self.current_theme_colors["bg"])])
        style.configure("TEntry", fieldbackground=self.current_theme_colors["entry_bg"], foreground=self.current_theme_colors["fg"])
        style.configure(
            "Treeview",
            background=self.current_theme_colors["tree_bg"],
            foreground=self.current_theme_colors["tree_fg"],
            fieldbackground=self.current_theme_colors["tree_bg"],
        )
        style.configure(
            "Treeview.Heading",
            background=self.current_theme_colors["tree_heading"],
            foreground=self.current_theme_colors["btn_fg"],
        )
        style.configure("TCombobox", fieldbackground=self.current_theme_colors["entry_bg"], foreground=self.current_theme_colors["fg"])

        for widget in self.winfo_children():
            self._update_widget_colors(widget)

    def _update_widget_colors(self, widget):
        try:
            if isinstance(widget, (tk.Label, ttk.Label)):
                widget.config(bg=self.current_theme_colors["bg"], fg=self.current_theme_colors["fg"])
            elif isinstance(widget, (tk.Frame, ttk.Frame, tk.LabelFrame, ttk.LabelFrame)):
                widget.config(bg=self.current_theme_colors["bg"], fg=self.current_theme_colors["fg"])
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            self._update_widget_colors(child)

    def set_theme(self, theme_name):
        logging.info(f"Setting theme to: {theme_name}")
        self.current_theme_name = theme_name
        self.current_theme_colors = PRESET_THEMES.get(theme_name, PRESET_THEMES["Default (Pink)"])
        self.data["theme"] = theme_name
        self.apply_theme()
        # Save theme setting to config file
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.data, f, indent=4)
        logging.debug("Theme setting saved to config file.")

    def create_widgets(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        # All style configurations are now handled by apply_theme to ensure consistency
        # and proper updates when the theme changes.

        # Move recent clips frame to top
        recent_clips_frame = ttk.LabelFrame(self, text="🎬 Recent Clips 🎬", relief=tk.RIDGE)
        recent_clips_frame.pack(padx=10, pady=10, fill="both", expand=True)
        cols_clips = ("Filename", "Size", "Uploaded")
        self.recent_clips_tree = ttk.Treeview(recent_clips_frame, columns=cols_clips, show="headings")
        for col in cols_clips:
            self.recent_clips_tree.heading(col, text=col)
            self.recent_clips_tree.column(col, width=150 if col == "Filename" else 100, anchor=tk.CENTER)
        self.recent_clips_tree.pack(fill="both", expand=True, padx=5, pady=5)

        button_frame_recent_clips = ttk.Frame(recent_clips_frame)
        button_frame_recent_clips.pack(pady=5, fill="x", expand=True)

        self.upload_selected_button = ttk.Button(
            button_frame_recent_clips, text="🚀 Upload Selected Clip", command=self.upload_selected_clip
        )
        self.upload_selected_button.pack(side=tk.LEFT, expand=True, padx=5)
        self.upload_selected_button.config(state=tk.DISABLED)

        self.preview_selected_button = ttk.Button(
            button_frame_recent_clips, text="👁️ Preview Selected Clip", command=self.preview_selected_clip
        )
        self.preview_selected_button.pack(side=tk.LEFT, expand=True, padx=5)
        self.preview_selected_button.config(state=tk.DISABLED)

        self.delete_selected_button = ttk.Button(
            button_frame_recent_clips, text="🗑️ Delete Selected Clip", command=self.delete_selected_clip
        )
        self.delete_selected_button.pack(side=tk.RIGHT, expand=True, padx=5)
        self.delete_selected_button.config(state=tk.DISABLED)

        self.recent_clips_tree.bind("<<TreeviewSelect>>", self._on_recent_clip_select)

        # Folder Stats frame at the bottom
        stats_frame = ttk.LabelFrame(self, text="✨ Folder Stats ✨", relief=tk.RIDGE)
        stats_frame.pack(padx=10, pady=10, fill="both", expand=True)
        cols = ("Folder", "Files", "Total Size", "Avg Size", "Top Format")
        self.stats_tree = ttk.Treeview(stats_frame, columns=cols, show="headings")
        for col in cols:
            self.stats_tree.heading(col, text=col)
            self.stats_tree.column(col, width=100)
        self.stats_tree.pack(fill="both", expand=True, padx=5, pady=5)

        button_frame = ttk.Frame(self)
        button_frame.pack(padx=10, pady=10, fill="x")
        save_button = ttk.Button(
            button_frame, text="💾 Save & Close", command=self.save_and_close
        )
        save_button.pack(side="left", expand=True, padx=5)
        refresh_button = ttk.Button(
            button_frame, text="🔄 Refresh Stats", command=self.populate_folder_stats
        )
        refresh_button.pack(side="right", expand=True, padx=5)

        self.credits_label = ttk.Label(
            self,
            text="6c75/luinbytes | github.com/luinbytes | Helped by Gemini CLI",
            font=("Arial", 8),
        )
        self.credits_label.pack(pady=(5, 0))

    def _on_recent_clip_select(self, event):
        logging.debug(f"Clip selection event triggered: {event}")
        selected_items = self.recent_clips_tree.selection()
        if selected_items:
            logging.debug(f"Clip selected: {self.recent_clips_tree.item(selected_items[0], 'tags')[0]}")
            self.upload_selected_button.config(state=tk.NORMAL)
            self.preview_selected_button.config(state=tk.NORMAL)
            self.delete_selected_button.config(state=tk.NORMAL) # Enable delete button
        else:
            logging.debug("No clip selected.")
            self.upload_selected_button.config(state=tk.DISABLED)
            self.preview_selected_button.config(state=tk.DISABLED)
            self.delete_selected_button.config(state=tk.DISABLED) # Disable delete button

    def preview_selected_clip(self):
        logging.info("Attempting to preview selected clip.")
        selected_item = self.recent_clips_tree.focus()
        if not selected_item:
            logging.warning("No clip selected for preview.")
            messagebox.showinfo("Preview", "No clip selected for preview.")
            return

        clip_path = self.recent_clips_tree.item(selected_item, "tags")[0]
        logging.debug(f"Clip path for preview: {clip_path}")

        if not os.path.exists(clip_path):
            logging.error(f"File not found for preview: {clip_path}")
            messagebox.showerror("Preview Error", f"File not found: {clip_path}")
            return

        try:
            os.startfile(clip_path)
            logging.info(f"Successfully opened clip for preview: {clip_path}")
        except Exception as e:
            logging.error(f"Could not open clip for preview {clip_path}: {e}", exc_info=True)
            messagebox.showerror("Preview Error", f"Could not open clip: {e}")

    def delete_selected_clip(self):
        logging.info("Attempting to delete selected clip.")
        selected_item = self.recent_clips_tree.focus()
        if not selected_item:
            logging.warning("No clip selected for deletion.")
            messagebox.showinfo("Delete", "No clip selected for deletion.")
            return

        clip_path = self.recent_clips_tree.item(selected_item, "tags")[0]
        clip_name = os.path.basename(clip_path)
        logging.debug(f"Clip path for deletion: {clip_path}, name: {clip_name}")

        if not os.path.exists(clip_path):
            logging.error(f"File not found for deletion: {clip_path}")
            messagebox.showerror("Delete Error", f"File not found: {clip_path}")
            self.populate_recent_clips() # Refresh recent clips as the file might be gone
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently delete '{clip_name}'?\nThis action cannot be undone and bypasses the recycle bin.",
            icon="warning"
        )
        if not confirm:
            logging.info("Deletion cancelled by user.")
            return

        try:
            os.remove(clip_path)
            logging.info(f"Successfully deleted clip: {clip_path}")

            # Remove from uploaded_files if present
            uploaded_files_list = self.data.get("uploaded_files", [])
            original_len = len(uploaded_files_list)
            self.data["uploaded_files"] = [entry for entry in uploaded_files_list if entry.get("name") != clip_name]
            if len(self.data["uploaded_files"]) < original_len:
                logging.debug(f"Removed '{clip_name}' from uploaded_files config.")
                with open(CONFIG_FILE, "w") as f:
                    json.dump(self.data, f, indent=4)
                logging.info("Updated config after deleting clip.")

            messagebox.showinfo("Delete Success", f"Clip '{clip_name}' deleted permanently.")
            self.populate_recent_clips() # Refresh the list

        except Exception as e:
            logging.error(f"Could not delete clip '{clip_name}' at {clip_path}: {e}", exc_info=True)
            messagebox.showerror("Delete Error", f"Could not delete clip '{clip_name}': {e}")

    def browse_video_base_dir(self):
        logging.info("Opening browse dialog for video base directory.")
        initial_dir = self.video_base_dir_var.get()
        if not os.path.isdir(initial_dir):
            logging.debug(f"Initial directory '{initial_dir}' not found, falling back to home directory.")
            initial_dir = os.path.expanduser("~")  # Fallback to home directory

        folder_selected = filedialog.askdirectory(initial_dir=initial_dir)
        if folder_selected:
            self.video_base_dir_var.set(folder_selected)
            logging.info(f"New video base directory selected: {folder_selected}")
        else:
            logging.info("Video base directory selection cancelled.")

    @staticmethod
    def format_size(size_bytes):
        logging.debug(f"Formatting size: {size_bytes} bytes")
        if size_bytes == 0:
            return "0 B"
        size_name = ("B", "KB", "MB", "GB", "TB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        formatted = f"{s} {size_name[i]}"
        logging.debug(f"Formatted size: {formatted}")
        return formatted

    def populate_folder_stats(self):
        logging.info("Populating folder stats.")
        for i in self.stats_tree.get_children():
            self.stats_tree.delete(i)
        logging.debug("Cleared existing folder stats entries.")

        # Use the configured video_base_dir
        video_base_dir = self.data.get("video_base_dir", SCRIPT_DIR)
        logging.debug(f"Using video_base_dir for folder stats: {video_base_dir}")

        if not os.path.isdir(video_base_dir):
            logging.error(f"Video base directory not found: {video_base_dir}. Cannot populate folder stats.")
            messagebox.showerror(
                "Error", f"Video base directory not found: {video_base_dir}"
            )
            return

        folders_in_base_dir = [
            d
            for d in os.listdir(video_base_dir)
            if os.path.isdir(os.path.join(video_base_dir, d)) and not d.startswith("$")
        ]
        logging.debug(f"Found {len(folders_in_base_dir)} subfolders to analyze in {video_base_dir}.")

        folder_data = []
        for folder_name in folders_in_base_dir:
            folder_path = os.path.join(
                video_base_dir, folder_name
            )  # Construct full path
            logging.debug(f"Analyzing folder: {folder_path}")
            video_files = []
            for ext in VIDEO_EXTENSIONS:
                found_in_ext = glob.glob(os.path.join(folder_path, "**", ext), recursive=True)
                video_files.extend(found_in_ext)
                if found_in_ext:
                    logging.debug(f"Found {len(found_in_ext)} files with {ext} in {folder_path}.")

            file_count = len(video_files)
            total_size = sum(os.path.getsize(f) for f in video_files)
            avg_size = total_size / file_count if file_count > 0 else 0
            extensions = [
                os.path.splitext(f)[1] for f in video_files if os.path.splitext(f)[1]
            ]
            top_ext = (
                max(set(extensions), key=extensions.count) if extensions else "N/A"
            )
            logging.debug(f"Folder '{folder_name}' - Files: {file_count}, Size: {total_size}, Avg Size: {avg_size}, Top Ext: {top_ext}")

            folder_data.append(
                {
                    "name": folder_name,
                    "file_count": file_count,
                    "total_size": total_size,
                    "avg_size": avg_size,
                    "top_ext": top_ext,
                }
            )

        # Sort by file_count (descending), then total_size (descending)
        folder_data.sort(key=lambda x: (x["file_count"], x["total_size"]), reverse=True)
        logging.debug("Folder data sorted.")

        for data in folder_data:
            self.stats_tree.insert(
                "",
                "end",
                values=(
                    data["name"],
                    data["file_count"],
                    self.format_size(data["total_size"]),
                    self.format_size(data["avg_size"]),
                    data["top_ext"],
                ),
            )
            logging.debug(f"Inserted folder stat: {data['name']}")
        logging.info("Folder stats population complete.")

    def save_and_close(self):
        logging.info("ConfigGUI save_and_close called. Destroying window.")
        # ConfigGUI no longer directly saves these, PreferencesWindow handles it.
        # This button now simply closes the window.
        self.destroy()

    def _on_num_recent_clips_change(self, event):
        logging.debug("_on_num_recent_clips_change called (placeholder).")
        # This method is now handled by the PreferencesWindow for its specific entry.
        # The main ConfigGUI's populate_recent_clips is called via callback from PreferencesWindow.
        pass

    def populate_recent_clips(self):
        logging.info("Populating recent clips.")
        for i in self.recent_clips_tree.get_children():
            self.recent_clips_tree.delete(i)
        logging.debug("Cleared existing recent clips entries.")

        # Re-fetch recent clips based on current settings
        video_base_dir = self.data.get("video_base_dir", SCRIPT_DIR)
        try:
            num_clips = int(self.data.get("num_recent_clips", "5"))
            if num_clips < 1:
                num_clips = 5 # Fallback if somehow invalid value persists
                logging.warning(f"Invalid num_recent_clips ({num_clips}), defaulting to 5.")
        except ValueError:
            num_clips = 5 # Fallback to default if invalid input
            logging.error(f"Failed to parse num_recent_clips, defaulting to 5.", exc_info=True)

        uploaded_files = self.data.get("uploaded_files", [])
        logging.debug(f"Fetching {num_clips} recent clips from {video_base_dir}. Uploaded files count: {len(uploaded_files)}.")
        self.recent_clips = get_recent_clips(video_base_dir, num_clips, uploaded_files, VIDEO_EXTENSIONS)
        logging.debug(f"Retrieved {len(self.recent_clips)} recent clips.")

        uploaded_files_data = self.data.get("uploaded_files", [])

        for clip in self.recent_clips:
            logging.debug(f"Processing recent clip: {clip['name']}")
            try:
                formatted_size = ConfigGUI.format_size(clip['size'])
            except TypeError:
                formatted_size = "N/A"
                logging.warning(f"Could not format size for clip {clip['name']}, size was {clip.get('size')}.")

            # Determine detailed upload status
            upload_entry = next((item for item in uploaded_files_data if item["name"] == clip["name"]), None)
            if upload_entry:
                if upload_entry["type"] == "manual":
                    uploaded_status = "✅ Manual"
                    logging.debug(f"Clip {clip['name']} marked as manually uploaded.")
                else: # Default to "Auto" or just "Uploaded"
                    uploaded_status = "✅ Auto"
                    logging.debug(f"Clip {clip['name']} marked as automatically uploaded.")
            else:
                uploaded_status = "❌"
                logging.debug(f"Clip {clip['name']} not marked as uploaded.")

            self.recent_clips_tree.insert(
                "",
                "end",
                values=(
                    clip["name"],
                    formatted_size,
                    uploaded_status,
                ),
                tags=(clip["path"],)
            )
            logging.debug(f"Inserted recent clip: {clip['name']}")
        self._on_recent_clip_select(None)
        logging.info("Recent clips population complete.")

    def upload_selected_clip(self):
        logging.info("Attempting to upload selected clip via button.")
        selected_item = self.recent_clips_tree.focus() # Get the selected item's ID
        if not selected_item:
            logging.warning("No clip selected for upload.")
            messagebox.showinfo("Upload", "No clip selected for upload.")
            return

        clip_path = self.recent_clips_tree.item(selected_item, "tags")[0]
        clip_name = os.path.basename(clip_path)
        logging.debug(f"Selected clip for manual upload: {clip_path}")

        sharex_host = self.data.get("sharex_host", "ezhost")
        logging.debug(f"ShareX host for manual upload: {sharex_host}")

        try:
            command = [SHAREX_PATH, clip_path, "-task", sharex_host]
            logging.debug(f"Executing ShareX command for manual upload: {command}")
            process = subprocess.run(
                command, capture_output=True, text=True, check=True
            )
            logging.info(f"ShareX manual upload successful for '{clip_name}'. Stdout: {process.stdout.strip()}")
            if process.stderr:
                logging.warning(f"ShareX Stderr for manual upload: {process.stderr.strip()}")


            # Update uploaded files
            uploaded_files = self.data.setdefault("uploaded_files", [])
            if not any(entry["name"] == clip_name for entry in uploaded_files):
                uploaded_files.append({"name": clip_name, "type": "manual"})
                logging.debug(f"Marked '{clip_name}' as manually uploaded in config.")
                with open(CONFIG_FILE, "w") as f:
                    json.dump(self.data, f, indent=4)
                logging.info("Config file updated after manual upload.")
            else:
                logging.debug(f"Clip '{clip_name}' already in uploaded_files.")

            messagebox.showinfo("Upload Success", f"Clip '{clip_name}' uploaded successfully!")

            # Refresh recent clips after upload
            logging.debug("Refreshing recent clips after manual upload.")
            video_base_dir = self.data.get("video_base_dir", SCRIPT_DIR)
            num_clips = int(self.data.get("num_recent_clips", "5"))
            uploaded_files_for_refresh = self.data.get("uploaded_files", []) # Get latest uploaded files
            self.recent_clips = get_recent_clips(video_base_dir, num_clips, uploaded_files_for_refresh, VIDEO_EXTENSIONS)
            self.populate_recent_clips()
            logging.info("Recent clips display refreshed.")

        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            error_message = f"Upload failed for '{clip_name}': {e}"
            if isinstance(e, subprocess.CalledProcessError):
                error_message += f"\nShareX Stdout: {e.stdout}"
                error_message += f"\nShareX Stderr: {e.stderr}"
            logging.error(f"Manual upload process failed for '{clip_name}': {error_message}", exc_info=True)
            messagebox.showerror("Upload Error", error_message)
        except Exception as e:
            logging.critical(f"An unexpected error occurred during manual upload of '{clip_name}': {e}", exc_info=True)
            messagebox.showerror("Critical Error", f"An unexpected error occurred during upload: {e}")

class ToastGUI(tk.Toplevel):
    def __init__(self, parent, clip_info, uploader, position, duration_s):
        super().__init__(parent)
        logging.debug(f"ToastGUI: Initializing for clip: {clip_info['name']}, uploader: {uploader}, position: {position}, duration: {duration_s}s")
        self.overrideredirect(True)
        # Use a generic theme color for toast to avoid issues if main window theme changes
        self.config(bg=PRESET_THEMES["Default (Pink)"]["bg"], borderwidth=2, relief="solid")
        self.attributes("-alpha", 0.0)
        self.attributes("-topmost", True)

        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack()
        ttk.Label(
            main_frame, text="6c75 Fast Uploader 🚀", font=("Arial", 12, "bold")
        ).pack(pady=(0, 10))
        ttk.Label(main_frame, text=f"✨ File: {clip_info['name']}").pack(anchor="w")
        ttk.Label(main_frame, text=f"📦 Size: {clip_info['size']}").pack(anchor="w")
        ttk.Label(main_frame, text=f"💌 To: {uploader}").pack(anchor="w")

        self.set_position(position)
        self.fade_in()
        self.after(int(duration_s * 1000), self.fade_out)
        logging.debug("ToastGUI: Widgets created and fade-in initiated.")


    def set_position(self, position):
        logging.debug(f"ToastGUI: Setting position to {position}.")
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width, height = self.winfo_width(), self.winfo_height()
        logging.debug(f"ToastGUI: Screen WxH: {screen_width}x{screen_height}, Toast WxH: {width}x{height}")

        if position == "Top Left":
            x, y = 10, 10
        elif position == "Top Right":
            x, y = screen_width - width - 10, 10
        elif position == "Bottom Left":
            x, y = 10, screen_height - height - 40
        else: # Bottom Right
            x, y = screen_width - width - 10, screen_height - height - 40
        self.geometry(f"{width}x{height}+{x}+{y}")
        logging.debug(f"ToastGUI: Geometry set to {width}x{height}+{x}+{y}.")

    def fade_in(self, alpha=0.0):
        if alpha < 1.0:
            alpha += 0.1
            self.attributes("-alpha", alpha)
            self.after(50, lambda: self.fade_in(alpha))
            logging.debug(f"ToastGUI: Fading in, current alpha: {alpha:.1f}")
        else:
            logging.debug("ToastGUI: Fade-in complete (alpha=1.0).")

    def fade_out(self, alpha=1.0):
        if alpha > 0.0:
            alpha -= 0.1
            self.attributes("-alpha", alpha)
            self.after(50, lambda: self.fade_out(alpha))
            logging.debug(f"ToastGUI: Fading out, current alpha: {alpha:.1f}")
        else:
            self.destroy()
            self.master.destroy()
            logging.info("ToastGUI: Toast faded out and destroyed.")


def get_recent_clips(base_dir, num_clips, uploaded_files_config, video_extensions):
    logging.debug(f"Getting {num_clips} recent clips from {base_dir}")
    all_video_files = []
    all_video_folders = [
        os.path.join(base_dir, d)
        for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d)) and not d.startswith("$")
    ]
    logging.debug(f"Found {len(all_video_folders)} subfolders in base directory.")

    for folder_path in all_video_folders:
        for ext in video_extensions:
            all_video_files.extend(
                glob.glob(os.path.join(folder_path, "**", ext), recursive=True)
            )

    all_video_files.sort(key=os.path.getmtime, reverse=True)

    recent_clips_info = []
    for clip_path in all_video_files[:num_clips]:
        clip_name = os.path.basename(clip_path)
        try:
            clip_size = os.path.getsize(clip_path)
            logging.debug(f"Clip size for {clip_name}: {clip_size} bytes")
        except FileNotFoundError:
            clip_size = 0
            logging.warning(f"Clip file not found: {clip_path}")

        # Check if the clip is in the uploaded_files list (which now contains dictionaries)
        is_uploaded = any(entry["name"] == clip_name for entry in uploaded_files_config)

        recent_clips_info.append({
            "path": clip_path,
            "name": clip_name,
            "size": clip_size,
            "uploaded": is_uploaded
        })
    logging.debug(f"Returning {len(recent_clips_info)} recent clips.")
    return recent_clips_info

def main():
    logging.info("Main function started.")
    # Define the old config path for migration
    old_config_path = os.path.join(os.getcwd(), CONFIG_FILE_NAME)

    # Ensure the target config directory exists
    os.makedirs(CONFIG_DIR, exist_ok=True)
    logging.debug(f"Config directory '{CONFIG_DIR}' ensured to exist.")

    # Migrate existing config file if it's in the old location and not yet in the new one
    if os.path.exists(old_config_path) and not os.path.exists(CONFIG_FILE):
        try:
            os.rename(old_config_path, CONFIG_FILE)
            logging.info(f"Migrated config file from {old_config_path} to {CONFIG_FILE}")
        except Exception as e:
            logging.error(f"Error migrating config file: {e}", exc_info=True)
            print(f"Error migrating config file: {e}")

    if not os.path.exists(CONFIG_FILE):
        logging.info("Config file not found. Creating a new one.")
        with open(CONFIG_FILE, "w") as f:
            json.dump(
                {
                    "sharex_host": "ezhost",
                    "toast_position": "Bottom Right",
                    "toast_duration": "5",
                    "uploaded_files": [], # This will now store list of dicts: [{"name": "clip.mp4", "type": "auto/manual"}]
                    "num_recent_clips": "5",
                    "video_base_dir": SCRIPT_DIR,
                    "theme": "Default (Pink)",
                    "debug_mode": False, # New debug mode setting
                },
                f,
                indent=4,
            )
        logging.info(f"Config file initialized at {CONFIG_FILE}")

    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)
    logging.info(f"Config loaded from {CONFIG_FILE}")
    if data.get("debug_mode", False):
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Debug mode loaded from config and enabled for main function.")
    else:
        logging.getLogger().setLevel(logging.INFO) # Ensure it's set if debug_mode is false

    video_base_dir = data.get("video_base_dir", SCRIPT_DIR)
    num_recent_clips = int(data.get("num_recent_clips", "5"))
    uploaded_files_config = data.get("uploaded_files", [])
    logging.debug(f"Loaded video_base_dir: {video_base_dir}, num_recent_clips: {num_recent_clips}")
    logging.debug(f"Loaded uploaded_files_config (raw): {uploaded_files_config}")

    # Robustly convert any old format (string) entries to new format (dict)
    cleaned_uploaded_files = []
    needs_config_update = False
    for entry in uploaded_files_config:
        if isinstance(entry, str):
            cleaned_uploaded_files.append({"name": entry, "type": "auto"})
            needs_config_update = True
            logging.debug(f"Migrated old string entry: {entry}")
        elif isinstance(entry, dict) and "name" in entry and "type" in entry:
            cleaned_uploaded_files.append(entry)
        else:
            logging.warning(f"Skipping malformed uploaded_files entry: {entry}")

    if needs_config_update:
        data["uploaded_files"] = cleaned_uploaded_files
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)
        uploaded_files_config = cleaned_uploaded_files # Update the reference to the cleaned list
        logging.info("Migrated old uploaded_files format and saved config.")

    uploaded_files_names = [entry["name"] for entry in uploaded_files_config]
    logging.debug(f"Uploaded files names: {uploaded_files_names}")

    all_video_files_in_base_dir = []
    all_video_folders = [  # These are full paths to sub-folders
        os.path.join(video_base_dir, d)
        for d in os.listdir(video_base_dir)
        if os.path.isdir(os.path.join(video_base_dir, d)) and not d.startswith("$")
    ]
    logging.debug(f"Found {len(all_video_folders)} potential video subfolders.")

    for folder_path in all_video_folders:
        for ext in VIDEO_EXTENSIONS:
            found_files = glob.glob(os.path.join(folder_path, "**", ext), recursive=True)
            all_video_files_in_base_dir.extend(found_files)
            if found_files:
                logging.debug(f"Found {len(found_files)} files with extension {ext} in {folder_path}")

    logging.info(f"Total video files found in base directory: {len(all_video_files_in_base_dir)}")

    recent_clips = get_recent_clips(video_base_dir, num_recent_clips, uploaded_files_config, VIDEO_EXTENSIONS)
    logging.debug(f"Fetched {len(recent_clips)} recent clips.")

    if not all_video_files_in_base_dir: # Check if there are ANY video files in base dir and its subfolders
        logging.info("No video files found in the base directory. Opening ConfigGUI.")
        ConfigGUI(data, recent_clips=recent_clips).mainloop()
        return

    absolute_latest_video = max(all_video_files_in_base_dir, key=os.path.getmtime)
    absolute_latest_video_name = os.path.basename(absolute_latest_video)
    logging.info(f"Absolute latest video: {absolute_latest_video_name}")

    if absolute_latest_video_name in uploaded_files_names:
        logging.info(f"Latest clip '{absolute_latest_video_name}' already uploaded. Opening ConfigGUI.")
        ConfigGUI(data, recent_clips=recent_clips).mainloop()
    else:
        sharex_host = data.get("sharex_host", "ezhost")
        logging.info(f"Latest clip '{absolute_latest_video_name}' not uploaded. Attempting to upload to {sharex_host}.")

        try:
            absolute_latest_video_path = os.path.abspath(absolute_latest_video)
            command = [SHAREX_PATH, absolute_latest_video_path, "-task", sharex_host]
            logging.debug(f"Executing ShareX command: {command}")
            process = subprocess.run(
                command, capture_output=True, text=True, check=True
            )
            logging.info(f"ShareX upload successful for '{absolute_latest_video_name}'. Stdout: {process.stdout.strip()}")
            if process.stderr:
                logging.warning(f"ShareX Stderr: {process.stderr.strip()}")

            data.setdefault("uploaded_files", []).append({"name": absolute_latest_video_name, "type": "auto"})
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f, indent=4)
            logging.debug(f"Added '{absolute_latest_video_name}' to uploaded_files as 'auto'.")

            root = tk.Tk()
            root.withdraw()
            clip_info = {
                "name": absolute_latest_video_name,
                "size": ConfigGUI.format_size(
                    os.path.getsize(absolute_latest_video)
                ),
            }
            duration = float(data.get("toast_duration", 5))
            logging.debug(f"Displaying toast for '{absolute_latest_video_name}'. Duration: {duration}s.")
            toast = ToastGUI(
                root,
                clip_info,
                sharex_host,
                data.get("toast_position", "Bottom Right"),
                duration,
            )
            toast.mainloop()
            logging.info("Toast displayed and mainloop for toast completed.")

        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            root = tk.Tk()
            root.withdraw()
            error_message = f"Upload failed: {e}"
            if isinstance(e, subprocess.CalledProcessError):
                error_message += f"\nShareX Stdout: {e.stdout}"
                error_message += f"\nShareX Stderr: {e.stderr}"
            logging.error(f"Upload process failed for '{absolute_latest_video_name}': {error_message}", exc_info=True)
            messagebox.showerror("Error", error_message)
            ConfigGUI(data, recent_clips=recent_clips).mainloop()
        except Exception as e:
            logging.critical(f"An unexpected error occurred in main upload logic: {e}", exc_info=True)
            messagebox.showerror("Critical Error", f"An unexpected error occurred: {e}")
            ConfigGUI(data, recent_clips=recent_clips).mainloop()


if __name__ == "__main__":
    main()
