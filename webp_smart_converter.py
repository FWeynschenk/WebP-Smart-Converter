import os
import threading
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image
from send2trash import send2trash

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORT = True
except ImportError:
    HEIC_SUPPORT = False


def delete_original(filepath):
    """Remove the original file, trashing it or permanently deleting it per the toggle."""
    if trash_var.get():
        send2trash(filepath)
    else:
        os.remove(filepath)


def get_webp_type(filepath):
    """Reads the WebP header to determine its chunk type."""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(16)
            if header[8:12] != b'WEBP':
                return None
            # Returns b'VP8 ', b'VP8L', or b'VP8X'
            return header[12:16]
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None


def get_unique_filename(filepath):
    """Generates a unique JPG filename to prevent overwriting duplicates."""
    base, _ = os.path.splitext(filepath)
    new_filepath = f"{base}.jpg"
    counter = 1
    while os.path.exists(new_filepath):
        new_filepath = f"{base}_{counter}.jpg"
        counter += 1
    return new_filepath


def collect_files(paths):
    """Expand directories recursively and collect all supported image files."""
    files = []
    for path in paths:
        if os.path.isdir(path):
            for root_dir, _, filenames in os.walk(path):
                for filename in filenames:
                    if filename.lower().endswith(('.webp', '.heic')):
                        files.append(os.path.join(root_dir, filename))
        elif os.path.isfile(path) and path.lower().endswith(('.webp', '.heic')):
            files.append(path)
    return files


def convert_file(file_path):
    """Convert a single file. Returns 'converted', 'skipped', or 'error'."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.heic':
        if not HEIC_SUPPORT:
            print(f"Skipping {file_path}: pillow-heif not installed.")
            return 'error'
        try:
            new_path = get_unique_filename(file_path)
            with Image.open(file_path) as img:
                img.convert('RGB').save(new_path, 'JPEG', quality=90)
            delete_original(file_path)
            return 'converted'
        except Exception as e:
            print(f"Failed to convert {file_path}: {e}")
            return 'error'

    elif ext == '.webp':
        webp_type = get_webp_type(file_path)
        # VP8L is lossless, VP8X is extended (alpha/metadata). These break old software.
        if webp_type in [b'VP8L', b'VP8X']:
            try:
                new_path = get_unique_filename(file_path)
                with Image.open(file_path) as img:
                    img.convert('RGB').save(new_path, 'JPEG', quality=90)
                delete_original(file_path)
                return 'converted'
            except Exception as e:
                print(f"Failed to convert {file_path}: {e}")
                return 'error'
        # VP8 is standard lossy — old software can open this fine.
        return 'skipped'

    return 'skipped'


def run_conversion(paths):
    """Collect and process files; update the progress bar on the main thread."""
    files = collect_files(paths)

    if not files:
        root.after(0, lambda: set_status("No supported files found."))
        return

    total = len(files)
    root.after(0, lambda: progress_bar.config(maximum=total, value=0))

    converted = skipped = errors = 0
    for i, file_path in enumerate(files, 1):
        name = os.path.basename(file_path)
        root.after(0, lambda n=name: set_status(f"Processing: {n}"))
        result = convert_file(file_path)
        if result == 'converted':
            converted += 1
        elif result == 'skipped':
            skipped += 1
        else:
            errors += 1
        root.after(0, lambda v=i: progress_bar.config(value=v))

    def finish():
        progress_bar.config(value=0)
        set_status("Drop files here or use the buttons below.")
        messagebox.showinfo(
            "Processing Complete",
            f"Converted to JPG:              {converted}\n"
            f"Compatible, skipped (VP8):     {skipped}\n"
            f"Errors:                        {errors}"
        )

    root.after(0, finish)


def start_conversion(paths):
    set_status("Starting…")
    threading.Thread(target=run_conversion, args=(paths,), daemon=True).start()


def on_drop(event):
    paths = root.tk.splitlist(event.data)
    start_conversion(paths)


def pick_files():
    filetypes = [
        ("Supported images", "*.webp *.heic"),
        ("WebP files", "*.webp"),
        ("HEIC files", "*.heic"),
        ("All files", "*.*"),
    ]
    paths = filedialog.askopenfilenames(title="Select files to convert", filetypes=filetypes)
    if paths:
        start_conversion(list(paths))


def pick_folder():
    path = filedialog.askdirectory(title="Select folder to convert")
    if path:
        start_conversion([path])


def set_status(text):
    status_label.config(text=text)


# ── UI ────────────────────────────────────────────────────────────────────────

BG = "#2d2d2d"
FG = "#ffffff"
ACCENT = "#4a90d9"
BTN_BG = "#3d3d3d"
FONT = ("Segoe UI", 11)

root = TkinterDnD.Tk()
root.title("WebP & HEIC Smart Converter")
root.geometry("480x300")
root.resizable(False, False)
root.config(bg=BG)

# Drop zone
drop_label = tk.Label(
    root,
    text=(
        "Drag & Drop .webp or .heic files / folders here\n\n"
        "WebP: only incompatible variants (Lossless/Alpha) are converted.\n"
        "HEIC: always converted to JPG."
    ),
    bg=BG,
    fg=FG,
    font=FONT,
    justify="center",
    relief="groove",
    bd=2,
    cursor="hand2",
)
drop_label.pack(fill=tk.BOTH, expand=True, padx=16, pady=(14, 8))

# Buttons
btn_frame = tk.Frame(root, bg=BG)
btn_frame.pack(fill=tk.X, padx=16, pady=(0, 8))

btn_style = dict(bg=BTN_BG, fg=FG, font=("Segoe UI", 10), relief="flat",
                 activebackground=ACCENT, activeforeground=FG, padx=12, pady=5, cursor="hand2")

tk.Button(btn_frame, text="Select Files…", command=pick_files, **btn_style).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))
tk.Button(btn_frame, text="Select Folder…", command=pick_folder, **btn_style).pack(side=tk.LEFT, expand=True, fill=tk.X)

# Trash toggle
trash_var = tk.BooleanVar(value=True)
tk.Checkbutton(
    root,
    text="Move originals to Recycle Bin (uncheck to delete permanently)",
    variable=trash_var,
    bg=BG, fg="#aaaaaa", selectcolor=BTN_BG,
    activebackground=BG, activeforeground=FG,
    font=("Segoe UI", 9),
    cursor="hand2",
    anchor="w",
).pack(fill=tk.X, padx=14, pady=(0, 4))

# Status + progress
status_label = tk.Label(root, text="Drop files here or use the buttons below.",
                        bg=BG, fg="#aaaaaa", font=("Segoe UI", 9), anchor="w")
status_label.pack(fill=tk.X, padx=16)

style = ttk.Style(root)
style.theme_use("default")
style.configure("dark.Horizontal.TProgressbar", troughcolor="#1a1a1a", background=ACCENT, thickness=10)

progress_bar = ttk.Progressbar(root, style="dark.Horizontal.TProgressbar",
                                orient="horizontal", mode="determinate", length=448)
progress_bar.pack(padx=16, pady=(2, 12))

if not HEIC_SUPPORT:
    status_label.config(text="Note: pillow-heif not installed — HEIC support disabled.", fg="#e07070")

root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

root.mainloop()
