import tkinter as tk
from tkinter import ttk
import apod_desktop
from tkcalendar import DateEntry
from PIL import ImageTk, Image
import os
import image_lib

# TODO: Create the GUI
script_dir = os.path.dirname(os.path.abspath(__file__))

def display_image(event=None):
    global image_to_set
    selected_image = image_var.get()
    info = apod_desktop.get_apod_info_from_title(selected_image)
    image_path = info['file_path']
    description = info['explantion']

    image_to_set = image_path
    image_one = Image.open(image_path)
    image_one = image_one.resize((400, 300))
    cached_image = ImageTk.PhotoImage(image_one)
    image_label.configure(image=cached_image, text="")
    description_label.config(text=description)
    image_label.image = cached_image

def set_as_desktop():
    # Placeholder for setting the desktop wallpaper
    image_lib.set_desktop_background_image(image_to_set)
    
# Create main window
root = tk.Tk()
root.title("Astronomy Picture of the Day Viewer")
root.geometry("800x600")
root.iconbitmap(os.path.join(script_dir, 'icon.ico'))

# Placeholder for the image
image_path = os.path.join(script_dir, 'nasa.png')
image_one = Image.open(image_path)
image_one = image_one.resize((400, 300))
photo = ImageTk.PhotoImage(image_one)
image_label = tk.Label(root, image=photo)
image_label.pack(pady=10)

# Image description label
description_label = tk.Label(root, wraplength=600, justify="left", text="", anchor="w")
description_label.pack(pady=5)

# Bottom frame for controls
bottom_frame = tk.Frame(root)
bottom_frame.pack(pady=10)

# Frame for "View Cached Image"
view_cached_frame = tk.LabelFrame(bottom_frame, text="View Cached Image")
view_cached_frame.grid(row=0, column=0, padx=5, pady=5)

# "Select Image" Label
select_image_label = tk.Label(view_cached_frame, text="Select Image:")
select_image_label.grid(row=0, column=0, padx=5, pady=5)

# Image Selection Dropdown
image_var = tk.StringVar(value="Select Image")
image_selection = ttk.Combobox(view_cached_frame, textvariable=image_var)
image_selection['values'] = apod_desktop.get_all_apod_title()
image_selection.grid(row=0, column=1, padx=5, pady=5)
image_selection.bind("<<ComboboxSelected>>", display_image)

# Set as Desktop Button
set_desktop_button = tk.Button(view_cached_frame, text="Set as Desktop", command=set_as_desktop)
set_desktop_button.grid(row=0, column=2, padx=5, pady=5)

# Run the application
root.mainloop()