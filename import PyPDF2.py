import fitz  # PyMuPDF
import re
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import sys
import pyperclip
import traceback
import os
from tkinter import Menu, LabelFrame
import webbrowser


# Initialize a global variable to store the path of the currently loaded PDF file
current_pdf_path = None

def browse_pdf_file():
    global current_pdf_path  # Declare that we are using the global variable
    current_pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    
    if current_pdf_path:
        identifier_pattern = r'\b[A-Z0-9]{10}\b'  # Adjust as needed
        try:
            anomalies = detect_anomalies(current_pdf_path, identifier_pattern)

            if anomalies:
                result_text.config(state=tk.NORMAL)
                result_text.delete('1.0', tk.END)
                for anomaly in anomalies:
                    result_text.insert(tk.END, anomaly + '\n')
                result_text.config(state=tk.DISABLED)
                messagebox.showinfo("Anomalies Found", "Anomalies found and displayed in the text box.")
            else:
                messagebox.showinfo("No Anomalies", "No anomalies found in the PDF file.")
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            error_info = f"Exception: {str(e)}\n"
            error_info += f"Traceback:\n{traceback.format_exc()}"
            pyperclip.copy(error_message + "\n\n" + error_info)
            messagebox.showerror("Error", error_message)
            sys.exit()

def detect_anomalies(pdf_path, identifier_pattern):
    anomalies = []

    pdf_document = fitz.open(pdf_path)

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        page_text = page.get_text()

        identifier_matches = re.finditer(identifier_pattern, page_text)
        for match in identifier_matches:
            anomalies.append(f"Unique Identifier on page {page_num + 1}: {match.group()}")

        double_space_pattern = r'\s{2,}'
        double_space_matches = re.finditer(double_space_pattern, page_text)
        for match in double_space_matches:
            anomalies.append(f"Double Spaces on page {page_num + 1}: '{match.group()}'")

        dot_pattern = r'\.{2,}'
        dot_matches = re.finditer(dot_pattern, page_text)
        for match in dot_matches:
            anomalies.append(f"Unnecessary Dots on page {page_num + 1}: '{match.group()}'")

        invisible_space_pattern = r'\u200B'
        invisible_space_matches = re.finditer(invisible_space_pattern, page_text)
        for match in invisible_space_matches:
            anomalies.append(f"Invisible Space on page {page_num + 1}: '{match.group()}'")

    pdf_document.close()

    return anomalies

def fix_anomalies(pdf_path, identifier_pattern):
    pdf_document = fitz.open(pdf_path)
    new_pdf_document = fitz.open()

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        page_text = page.get_text()

        # Replace anomalies
        page_text = re.sub(r'\s{2,}', ' ', page_text)
        page_text = re.sub(r'\.{2,}', '.', page_text)
        page_text = re.sub(r'\u200B', '', page_text)

        new_page = new_pdf_document.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_text((50, 50), page_text)

    new_pdf_path = "fixed.pdf"
    new_pdf_document.save(new_pdf_path)
    new_pdf_document.close()
    pdf_document.close()

    folder_path = os.path.dirname(os.path.abspath(new_pdf_path))
    open_folder(folder_path)

    return new_pdf_path

def fix_pdf():
    global current_pdf_path  # Declare that we are using the global variable
    if not current_pdf_path:
        messagebox.showwarning("No File", "No PDF file is currently loaded. Please browse and load a file first.")
        return

    identifier_pattern = r'\b[A-Z0-9]{10}\b'  # Adjust as needed
    try:
        fixed_pdf_path = fix_anomalies(current_pdf_path, identifier_pattern)
        messagebox.showinfo("Fix Complete", "Anomalies have been fixed in the PDF file.")
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        error_info = f"Exception: {str(e)}\n"
        error_info += f"Traceback:\n{traceback.format_exc()}"
        pyperclip.copy(error_message + "\n\n" + error_info)
        messagebox.showerror("Error", error_message)
        sys.exit()

def open_folder(folder_path):
    if os.name == 'nt':  # For Windows
        os.startfile(folder_path)
    elif os.uname()[0] == 'Darwin':  # For macOS
        os.system(f'open "{folder_path}"')
    else:  # For Linux
        os.system(f'xdg-open "{folder_path}"')

root = tk.Tk()
root.title("PDF Analyzer and Fixer")

def open_github():
    webbrowser.open("https://github.com/wortkraecker/PDFanomalyDetect")

def toggle_about():
    if about_frame.winfo_ismapped():
        about_frame.pack_forget()
    else:
        about_frame.pack(fill=tk.BOTH, expand=tk.YES)

label = tk.Label(root, text="Select a PDF file:")
label.pack()

# Create a Menu bar
menu_bar = Menu(root)
root.config(menu=menu_bar)
update_menu = Menu(menu_bar, tearoff=0)  # Rename the menu to better match its function
menu_bar.add_cascade(label='Check for update', menu=update_menu)
update_menu.add_command(label='GitHub', command=open_github)

about_frame = LabelFrame(root, text="About", padx=5, pady=5)
about_label = tk.Label(about_frame, text="PDF Analyzer and Fixer\nVersion: 1.0\nWortkraecker\nBuild: 26092023")
about_label.pack(padx=10, pady=10)
about_frame.pack(side=tk.BOTTOM, fill=tk.X)

browse_button = tk.Button(root, text="Browse", command=browse_pdf_file)
browse_button.pack()

result_text = tk.Text(root, wrap=tk.WORD, state=tk.DISABLED)
result_text.pack()

fix_button = tk.Button(root, text="Fix Anomalies", command=fix_pdf)
fix_button.pack()

root.mainloop()
