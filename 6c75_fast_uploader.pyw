import os
import glob
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_NAME = "fast_uploader.json"
CONFIG_DIR = os.path.join(os.path.expanduser("~"), "Documents")
CONFIG_FILE = os.path.join(CONFIG_DIR, CONFIG_FILE_NAME)
SHAREX_PATH = r"C:\Program Files\ShareX\ShareX.exe"
VIDEO_EXTENSIONS = ("*.mp4", "*.mkv", "*.mov", "*.avi", "*.wmv")

THEME = {
    "bg": "#FFC0CB",
    "fg": "#5D4037",
    "btn_bg": "#FF69B4",
    "btn_fg": "#FFFFFF",
    "entry_bg": "#FFF0F5",
    "tree_bg": "#FFF0F5",
    "tree_fg": "#5D4037",
    "tree_heading": "#FF69B4",
}


class ConfigGUI(tk.Tk):
    def __init__(self, data):
        super().__init__()
        self.title("6c75 Fast Uploader Settings")
        self.geometry("600x550")
        self.config(bg=THEME["bg"])
        self.data = data
        self.create_widgets()
        self.populate_folder_stats()

    def create_widgets(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel", background=THEME["bg"], foreground=THEME["fg"])
        style.configure("TFrame", background=THEME["bg"])
        style.configure(
            "TButton",
            background=THEME["btn_bg"],
            foreground=THEME["btn_fg"],
            borderwidth=1,
        )
        style.map("TButton", background=[("active", THEME["bg"])])
        style.configure("TEntry", fieldbackground=THEME["entry_bg"])
        style.configure(
            "Treeview",
            background=THEME["tree_bg"],
            foreground=THEME["tree_fg"],
            fieldbackground=THEME["tree_bg"],
        )
        style.configure(
            "Treeview.Heading",
            background=THEME["tree_heading"],
            foreground=THEME["btn_fg"],
        )
        style.configure("TCombobox", fieldbackground=THEME["entry_bg"])

        stats_frame = ttk.LabelFrame(self, text="✨ Folder Stats ✨", relief=tk.RIDGE)
        stats_frame.pack(padx=10, pady=10, fill="both", expand=True)
        cols = ("Folder", "Files", "Total Size", "Avg Size", "Top Format")
        self.stats_tree = ttk.Treeview(stats_frame, columns=cols, show="headings")
        for col in cols:
            self.stats_tree.heading(col, text=col)
            self.stats_tree.column(col, width=100)
        self.stats_tree.pack(fill="both", expand=True, padx=5, pady=5)

        settings_frame = ttk.Frame(self)
        settings_frame.pack(padx=10, pady=5, fill="x", expand=True)

        host_frame = ttk.LabelFrame(settings_frame, text="💌 ShareX Host 💌")
        host_frame.pack(side="left", expand=True, padx=(0, 5), fill="x")
        self.host_var = tk.StringVar(value=self.data.get("sharex_host", "ezhost"))
        self.host_entry = ttk.Entry(host_frame, textvariable=self.host_var)
        self.host_entry.pack(fill="x", padx=5, pady=5)

        toast_frame = ttk.LabelFrame(settings_frame, text="📍 Toast Position 📍")
        toast_frame.pack(side="left", expand=True, padx=5, fill="x")
        self.toast_pos_var = tk.StringVar(
            value=self.data.get("toast_position", "Bottom Right")
        )
        self.toast_pos_combo = ttk.Combobox(
            toast_frame,
            textvariable=self.toast_pos_var,
            values=["Top Left", "Top Right", "Bottom Left", "Bottom Right"],
            state="readonly",
        )
        self.toast_pos_combo.pack(fill="x", padx=5, pady=5)

        duration_frame = ttk.LabelFrame(settings_frame, text="⏱️ Toast Duration (s) ⏱️")
        duration_frame.pack(side="left", expand=True, padx=(5, 0), fill="x")
        self.toast_duration_var = tk.StringVar(
            value=self.data.get("toast_duration", "5")
        )
        self.toast_duration_entry = ttk.Entry(
            duration_frame, textvariable=self.toast_duration_var
        )
        self.toast_duration_entry.pack(fill="x", padx=5, pady=5)

        video_dir_frame = ttk.LabelFrame(self, text="📁 Video Base Directory 📁")
        video_dir_frame.pack(padx=10, pady=5, fill="x")
        self.video_base_dir_var = tk.StringVar(
            value=self.data.get("video_base_dir", SCRIPT_DIR)
        )
        video_dir_entry = ttk.Entry(
            video_dir_frame, textvariable=self.video_base_dir_var
        )
        video_dir_entry.pack(side="left", fill="x", expand=True, padx=(5, 0), pady=5)
        browse_button = ttk.Button(
            video_dir_frame, text="Browse", command=self.browse_video_base_dir
        )
        browse_button.pack(side="right", padx=(0, 5), pady=5)

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

        credits_label = ttk.Label(
            self,
            text="6c75/luinbytes | github.com/luinbytes | Helped by Gemini CLI",
            background=THEME["bg"],
            foreground=THEME["fg"],
            font=("Arial", 8),
        )
        credits_label.pack(pady=(5, 0))

    def browse_video_base_dir(self):
        initial_dir = self.video_base_dir_var.get()
        if not os.path.isdir(initial_dir):
            initial_dir = os.path.expanduser("~")  # Fallback to home directory

        folder_selected = filedialog.askdirectory(initialdir=initial_dir)
        if folder_selected:
            self.video_base_dir_var.set(folder_selected)

    def format_size(self, size_bytes):
        if size_bytes == 0:
            return "0 B"
        size_name = ("B", "KB", "MB", "GB", "TB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"

    def populate_folder_stats(self):
        for i in self.stats_tree.get_children():
            self.stats_tree.delete(i)

        # Use the configured video_base_dir
        video_base_dir = self.data.get("video_base_dir", SCRIPT_DIR)

        if not os.path.isdir(video_base_dir):
            messagebox.showerror(
                "Error", f"Video base directory not found: {video_base_dir}"
            )
            return

        folders_in_base_dir = [  # These are the folder *names* within the base dir
            d
            for d in os.listdir(video_base_dir)
            if os.path.isdir(os.path.join(video_base_dir, d)) and not d.startswith("$")
        ]

        folder_data = []
        for folder_name in folders_in_base_dir:
            folder_path = os.path.join(
                video_base_dir, folder_name
            )  # Construct full path
            video_files = [
                f
                for ext in VIDEO_EXTENSIONS
                for f in glob.glob(os.path.join(folder_path, "**", ext), recursive=True)
            ]

            file_count = len(video_files)
            total_size = sum(os.path.getsize(f) for f in video_files)
            avg_size = total_size / file_count if file_count > 0 else 0
            extensions = [
                os.path.splitext(f)[1] for f in video_files if os.path.splitext(f)[1]
            ]
            top_ext = (
                max(set(extensions), key=extensions.count) if extensions else "N/A"
            )

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

    def save_and_close(self):
        self.data["sharex_host"] = self.host_var.get()
        self.data["toast_position"] = self.toast_pos_var.get()
        self.data["toast_duration"] = self.toast_duration_var.get()
        self.data["video_base_dir"] = self.video_base_dir_var.get()  # Save new setting
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.data, f, indent=4)
        self.destroy()


class ToastGUI(tk.Toplevel):
    def __init__(self, parent, clip_info, uploader, position, duration_s):
        super().__init__(parent)
        self.overrideredirect(True)
        self.config(bg=THEME["bg"], borderwidth=2, relief="solid")
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

    def set_position(self, position):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width, height = self.winfo_width(), self.winfo_height()

        if position == "Top Left":
            x, y = 10, 10
        elif position == "Top Right":
            x, y = screen_width - width - 10, 10
        elif position == "Bottom Left":
            x, y = 10, screen_height - height - 40
        else:
            x, y = screen_width - width - 10, screen_height - height - 40
        self.geometry(f"{width}x{height}+{x}+{y}")

    def fade_in(self, alpha=0.0):
        if alpha < 1.0:
            alpha += 0.1
            self.attributes("-alpha", alpha)
            self.after(50, lambda: self.fade_in(alpha))

    def fade_out(self, alpha=1.0):
        if alpha > 0.0:
            alpha -= 0.1
            self.attributes("-alpha", alpha)
            self.after(50, lambda: self.fade_out(alpha))
        else:
            self.destroy()
            self.master.destroy()


def main():
    # Define the old config path for migration
    old_config_path = os.path.join(os.getcwd(), CONFIG_FILE_NAME)

    # Ensure the target config directory exists
    os.makedirs(CONFIG_DIR, exist_ok=True)

    # Migrate existing config file if it's in the old location and not yet in the new one
    if os.path.exists(old_config_path) and not os.path.exists(CONFIG_FILE):
        try:
            os.rename(old_config_path, CONFIG_FILE)
            print(f"Migrated config file from {old_config_path} to {CONFIG_FILE}")
        except Exception as e:
            print(f"Error migrating config file: {e}")

    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump(
                {
                    "sharex_host": "ezhost",
                    "toast_position": "Bottom Right",
                    "toast_duration": "5",
                    "uploaded_files": [],
                    "video_base_dir": SCRIPT_DIR,  # New setting
                },
                f,
                indent=4,
            )

    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)

    video_base_dir = data.get("video_base_dir", SCRIPT_DIR)  # Get video base directory

    all_video_folders = [  # These are full paths to sub-folders
        os.path.join(video_base_dir, d)
        for d in os.listdir(video_base_dir)
        if os.path.isdir(os.path.join(video_base_dir, d)) and not d.startswith("$")
    ]

    video_files = []
    for folder_path in all_video_folders:
        for ext in VIDEO_EXTENSIONS:
            video_files.extend(
                glob.glob(os.path.join(folder_path, "**", ext), recursive=True)
            )

    if not video_files:
        ConfigGUI(data).mainloop()
        return

    absolute_latest_video = max(video_files, key=os.path.getmtime)
    absolute_latest_video_name = os.path.basename(absolute_latest_video)

    uploaded_files = data.get("uploaded_files", [])

    if absolute_latest_video_name in uploaded_files:
        ConfigGUI(data).mainloop()
    else:
        sharex_host = data.get("sharex_host", "ezhost")

        try:
            absolute_latest_video_path = os.path.abspath(absolute_latest_video)
            command = [SHAREX_PATH, absolute_latest_video_path, "-task", sharex_host]
            process = subprocess.run(
                command, capture_output=True, text=True, check=True
            )
            data.setdefault("uploaded_files", []).append(absolute_latest_video_name)
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f, indent=4)

            root = tk.Tk()
            root.withdraw()
            clip_info = {
                "name": absolute_latest_video_name,
                "size": ConfigGUI.format_size(
                    None, os.path.getsize(absolute_latest_video)
                ),
            }
            duration = float(data.get("toast_duration", 5))
            toast = ToastGUI(
                root,
                clip_info,
                sharex_host,
                data.get("toast_position", "Bottom Right"),
                duration,
            )
            toast.mainloop()

        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            root = tk.Tk()
            root.withdraw()
            error_message = f"Upload failed: {e}"
            if isinstance(e, subprocess.CalledProcessError):
                error_message += f"\nShareX Stdout: {e.stdout}"
                error_message += f"\nShareX Stderr: {e.stderr}"
            messagebox.showerror("Error", error_message)
            ConfigGUI(data).mainloop()


if __name__ == "__main__":
    main()
