import os
import shutil
import threading
from PIL import Image

import tkinter as tk
from tkinter import filedialog, ttk

class FileUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Folder Uploader")
        self.root.geometry("600x400")

        self.photo_upload = tk.PhotoImage(file='C:/Users/Pero/Desktop/Python-projekti/Recompress Photo Albums/Icons/upload.png')
        self.photo_upload_resized = self.photo_upload.subsample(12,12)

        self.photo_processing = tk.PhotoImage(file='C:/Users/Pero/Desktop/Python-projekti/Recompress Photo Albums/Icons/engineering.png')
        self.photo_processing_resized = self.photo_processing.subsample(12,12)

        self.upload_button = ttk.Button(root, text="Upload Folder", command=self.upload_folder, image=self.photo_upload_resized)
        self.upload_button.pack(pady=20)

        self.process_button = ttk.Button(root, text="Process Folder", command=self.process_folder, image=self.photo_processing_resized)
        self.process_button.pack(pady=10)

        self.clear_button = ttk.Button(root, text="Clear Text", command=self.clear_text)
        self.clear_button.place(relx=0.98, rely=1.0, anchor='se', x=-10, y=-10)

        self.folder_path_label = ttk.Label(root, text="No folder selected")
        self.folder_path_label.pack(pady=10)

        self.scrollbar = ttk.Scrollbar(root)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.message_text = tk.Text(root, height=10, width=50, yscrollcommand=self.scrollbar.set)
        self.message_text.pack(pady=20)
        self.scrollbar.config(command=self.message_text.yview)

        self.folder_path = None

    def upload_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.folder_path_label.config(text=self.folder_path)
        else:
            self.folder_path_label.config(text="No folder selected")

    def _process_folder_thread(self):
        try:
            work(self.folder_path, self.message_text)
            self.message_text.insert(tk.END, "Work completed successfully.\n")
        except Exception as e:
            self.message_text.insert(tk.END, f"Error during processing: {str(e)}\n")

    def process_folder(self):
        if self.folder_path:
            self.message_text.insert(tk.END, "Processing folder...\n")
            self.root.update()
            process_thread = threading.Thread(target=self._process_folder_thread)
            process_thread.start()
        else:
            self.message_text.insert(tk.END, "Please select a folder first.\n")

    def clear_text(self):
        self.message_text.delete('1.0', tk.END)

    def get_folder_path(self):
        return self.folder_path
    
def copy_files(src_folder, dest_folder):
    if not os.path.exists(src_folder):
        print(f"Source folder '{src_folder}' does not exist.")
        return

    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
        print(f"Destination folder '{dest_folder}' created.")

    files = os.listdir(src_folder)

    for file_name in files:
        src_file = os.path.join(src_folder, file_name)
        dest_file = os.path.join(dest_folder, file_name)

        if os.path.isfile(src_file):
            shutil.copy(src_file, dest_file)
            print(f"Copied '{src_file}' to '{dest_file}'")
        else:
            print(f"Skipped '{src_file}' (not a file)")
    
def compress_image(image_path, output_path, quality):
    with Image.open(image_path) as img:
        img.save(output_path, "JPEG", optimize=True, quality=quality)

def compress_images_in_folder(folder_path, output_folder_path, quality):
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, filename)
            output_path = os.path.join(output_folder_path, filename)

            #print(f'Compressing {image_path}...')
            compress_image(image_path, output_path, quality)
            #print(f'Saved compressed image to {output_path}')

def delete_original_folder(folder_path):
    try:
        shutil.rmtree(folder_path)
        print(f'Source folder {folder_path} has been deleted.')
    except Exception as e:
        print(f'Error deleting source folder: {e}')

def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)
    return total_size
    
def work(original_folder_path, message_text):
    original_folder_name = os.path.basename(os.path.normpath(original_folder_path))
    original_folder_size_in_bytes = get_folder_size(original_folder_path)
    original_folder_size_in_MB = original_folder_size_in_bytes / (1024*1024)

    temp_folder_name = original_folder_name + "-temp"
    temp_folder_path = os.path.join(os.path.dirname(original_folder_path), temp_folder_name)
    os.makedirs(temp_folder_path, exist_ok=True)

    output_folder_path = original_folder_path

    message_text.insert(tk.END, "Copying files...\n")
    copy_files(original_folder_path, temp_folder_path)
    delete_original_folder(original_folder_path)

    quality = 50
    message_text.insert(tk.END, "Compressing images...\n")
    compress_images_in_folder(temp_folder_path, output_folder_path, quality)
    delete_original_folder(temp_folder_path)

    output_folder_size_in_bytes = get_folder_size(output_folder_path)
    output_folder_size_in_MB = output_folder_size_in_bytes / (1024*1024)

    compress_rate = (1-(output_folder_size_in_bytes/original_folder_size_in_bytes)) * 100
    message_text.insert(tk.END, f"Folder size before compressing: {original_folder_size_in_MB:.2f} MB\n")
    message_text.insert(tk.END, f"Folder size after compressing: {output_folder_size_in_MB:.2f} MB\n")
    message_text.insert(tk.END, f"Compressing saved {compress_rate:.2f}% of space\n")

    message_text.insert(tk.END, "Process completed.\n")


if __name__ == '__main__':
    root = tk.Tk()
    app = FileUploaderApp(root)
    root.mainloop()
    #folder_path = app.get_folder_path()
    #work(folder_path)