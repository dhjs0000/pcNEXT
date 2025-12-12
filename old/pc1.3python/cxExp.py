import os
import tkinter as tk
from tkinter import filedialog

def restore_file_explorer():
    # Your code here
    # Implementing a file explorer
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()
    file_list = os.listdir(folder_path)
    for file in file_list:
        print(file)

# Create a Tkinter window to display the file explorer
window = tk.Tk()
window.mainloop()
