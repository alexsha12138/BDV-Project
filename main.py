import tkinter as tk
from tkinter import filedialog
import pandas as pd
import os

def main():

    root = tk.Tk()
    root.title("Placeholder GUI Name")

    root.geometry("1280x720")
    root.configure(bg="#e6e6fa")

# GUI title/label
    label = tk.Label(root, text= "Placeholder Name", font=("Helvetica", 18, "bold"), bg="#e6e6fa", fg="black")
    label.pack(pady=(30,10))

# Divider
    H_line = tk.Frame (root, height = 2, width = 1000, bg = "black")
    H_line.pack(pady=(0,30))

# File upload button
    button_frame = tk.Frame(root, bg = "#e6e6fa")
    button_frame.pack(anchor = "w", padx=140)

    upload_button = tk.Button(button_frame, text = "Upload", font = ("Arial", 12), command = lambda: csv_upload(status_label, output_box))
    upload_button.pack(side = "left", padx=10)

    status_label = tk.Label(button_frame, text = "Please upload a CSV file", font = ("Arial", 12), bg = "#e6e6fa", fg = "black")
    status_label.pack(side="left", padx=10)

# column header output
    output_frame = tk.Frame(root, bg="#e6e6fa")
    output_frame.pack(anchor="w", padx=140, pady=(30,10))

    # set up scroll bar
    yscroll = tk.Scrollbar(output_frame, orient = "vertical")
    yscroll.pack(side = "right", fill = "y")
    xscroll = tk.Scrollbar(output_frame, orient = "horizontal")
    xscroll.pack(side="bottom", fill="x")

    output_box = tk.Text(output_frame, 
                         width=30, 
                         height=20, 
                         font=("Arial", 12),
                         yscrollcommand=yscroll.set,
                         xscrollcommand=xscroll.set,
                         wrap="none"
                         )
    output_box.pack(side="left", fill="both", expand=True)
    
    # configuring scroll bars
    yscroll.config(command=output_box.yview)
    xscroll.config(command=output_box.xview)

# Run GUI
    root.mainloop()



def csv_upload(status_label, output_box):
    file_path = filedialog.askopenfilename(
        title = "Select CSV File",
        filetypes=[("CSV Files","*.csv")]
    )
    if file_path:
        try:
            filename = os.path.basename(file_path)
            status_label.config(text=f"File selected: {filename}", fg="green")

            data = pd.read_csv(file_path)
            headers = data.columns.tolist()

            output_box.delete("1.0", tk.END) # clear box
            output_box.insert(tk.END, "\n  Variables:\n\n")

            for i in headers:
                output_box.insert(tk.END, f"  -  {i}\n")
        # handeling file reading errors/exceptions
        except Exception as e:
            status_label.config(text = "Error reading file, please check CSV", fg="red")
            output_box.delete("1.0", tk.END)
            output_box.insert(tk.END, str(e))

    else:
        status_label.config(text="Please upload a CSV file", fg="black")

if __name__ == "__main__":
    main()