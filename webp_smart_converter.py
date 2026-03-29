import os
import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image

def get_webp_type(filepath):
    """Reads the WebP header to determine its chunk type."""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(16)
            # Check if it's a valid WebP file
            if header[8:12] != b'WEBP':
                return None
            # Returns b'VP8 ', b'VP8L', or b'VP8X'
            return header[12:16]
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def get_unique_filename(filepath):
    """Generates a unique JPG filename to prevent overwriting duplicates."""
    base, ext = os.path.splitext(filepath)
    new_filepath = f"{base}.jpg"
    counter = 1
    while os.path.exists(new_filepath):
        new_filepath = f"{base}_{counter}.jpg"
        counter += 1
    return new_filepath

def process_files(event):
    # tkinterdnd2 splits the dragged files cleanly, even if paths have spaces
    files = root.tk.splitlist(event.data)
    converted_count = 0
    skipped_count = 0
    error_count = 0

    for file_path in files:
        if not file_path.lower().endswith('.webp'):
            continue

        webp_type = get_webp_type(file_path)

        # VP8L is lossless, VP8X is extended (alpha/metadata). These break old software.
        if webp_type in [b'VP8L', b'VP8X']:
            try:
                new_path = get_unique_filename(file_path)
                with Image.open(file_path) as img:
                    # Convert to RGB (JPG does not support transparency/alpha channels)
                    rgb_im = img.convert('RGB')
                    rgb_im.save(new_path, 'JPEG', quality=90)

                # Delete original webp upon successful save
                os.remove(file_path)
                converted_count += 1
            except Exception as e:
                print(f"Failed to convert {file_path}: {e}")
                error_count += 1

        # VP8 is standard lossy. Old software can likely open this.
        elif webp_type == b'VP8 ':
            skipped_count += 1

    messagebox.showinfo(
        "Processing Complete",
        f"Incompatible Converted to JPG: {converted_count}\n"
        f"Compatible Skipped (Kept as WebP): {skipped_count}\n"
        f"Errors: {error_count}"
    )

# Setup the Drag and Drop GUI
root = TkinterDnD.Tk()
root.title("WebP Smart Converter")
root.geometry("450x250")
root.config(bg="#2d2d2d")

label = tk.Label(
    root,
    text="Drag & Drop .webp files here\n\n"
         "Only incompatible WebPs (Lossless/Alpha)\n"
         "will be converted to JPG and deleted.",
    bg="#2d2d2d",
    fg="#ffffff",
    font=("Segoe UI", 12)
)
label.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

# Register the drop target
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', process_files)

root.mainloop()
