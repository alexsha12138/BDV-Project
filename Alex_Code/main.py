import tkinter as tk
from tkinter import filedialog
import pandas as pd
import os
from plotter import Plotter



data = None # global variable

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

    upload_button = tk.Button(button_frame, text = "Upload", font = ("Arial", 12), command = lambda: csv_upload(status_label, output_box, x_dropdown, y_dropdown, x_var, y_var))
    upload_button.pack(side = "left", padx=10)

    status_label = tk.Label(button_frame, text = "Please upload a CSV file", font = ("Arial", 12), bg = "#e6e6fa", fg = "black")
    status_label.pack(side="left", padx=10)

# content frame
    content_frame = tk.Frame(root,bg="#e6e6fa")
    content_frame.pack(padx=140, pady=(10,0), anchor="nw")


# column header output
    output_frame = tk.Frame(content_frame, bg="#e6e6fa")
    #output_frame.pack(anchor="w", padx=140, pady=(30,10))
    output_frame.pack(side="left", fill="both", expand=True)

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

# drop down to select variables for plotting

    # create frame
    dropdown_frame = tk.Frame(content_frame, bg="#e6e6fa")
    dropdown_frame.pack(side="left", padx=(20,0), anchor="n")

    # creaste variables to store selected values
    x_var = tk.StringVar()
    y_var = tk.StringVar()

    # x var
    x_label = tk.Label(dropdown_frame, text = "x-variable: ", font = ("Arial", 12), bg = "#e6e6fa")
    x_label.grid(row=0, column=0, sticky="w", pady=(0,10))

    x_dropdown = tk.OptionMenu(dropdown_frame, x_var, "")
    x_dropdown.config(width=20)
    x_dropdown.grid(row=0, column=1, pady=(0,10),  padx=(10,0))

    # y var
    y_label = tk.Label(dropdown_frame, text = "y-variable: ", font=("Arial", 12), bg="#e6e6fa")
    y_label.grid(row=1, column=0, sticky = "w")

    y_dropdown = tk.OptionMenu(dropdown_frame, y_var, "")
    y_dropdown.config(width=20)
    y_dropdown.grid(row=1, column=1, padx=(10,0))  

    # plot button
    plot_button= tk.Button(
        content_frame, 
        text="Plot", 
        font=("Arial", 12), 
        width = 12,
        command=lambda: handle_plot(x_var, y_var, xres_entry, yres_entry)
        )
    plot_button.pack(side="bottom")

    # x and y resolution of plot
    # x
    res_frame = tk.Frame(dropdown_frame, bg="#e6e6fa")
    res_frame.grid(row=2, column=0, columnspan=4, pady=(30, 0), sticky="w")

    xres_label = tk.Label(res_frame, text = "Resolution: ", font=("Arial", 12), bg="#e6e6fa")
    xres_label.grid(row=1, column = 0, sticky="w", pady=(20,10))

    xres_entry = tk.Entry(res_frame, font = ("Arial", 12), width=12)
    xres_entry.insert(0, "1280")
    xres_entry.grid(row=1, column=1, pady=(20,10), padx=(10, 10))
    
    # y
    yres_label = tk.Label(res_frame, text="x", font=("Arial", 12), bg="#e6e6fa")
    yres_label.grid(row=1, column=2, sticky="w", pady=(20, 10))

    yres_entry = tk.Entry(res_frame, font=("Arial", 12), width=12)
    yres_entry.insert(0, "720")  # default value
    yres_entry.grid(row=1, column=3, pady=(20, 10), padx=(10, 0))

    # plot titles & labels

    # title
    title_label = tk.Label(res_frame, text="Title:", font=("Arial", 12), bg="#e6e6fa")
    title_label.grid(row=2, column=0, sticky="w", pady=(10, 5))

    title_entry = tk.Entry(res_frame, font=("Arial", 12), width=35)
    title_entry.grid(row=2, column=1, columnspan=3, pady=(10, 5), padx=(10, 0))

    # x label
    xlabel_label = tk.Label(res_frame, text = "x label: ", font=("Arial", 12), bg="#e6e6fa")
    xlabel_label.grid(row=3, column=0, sticky="w", pady=(5, 5))

    xlabel_entry = tk.Entry(res_frame, font=("Arial", 12), width=35)
    xlabel_entry.grid(row=3, column=1, columnspan=3, pady=(5, 5), padx=(10, 0))

    # y label
    ylabel_label = tk.Label(res_frame, text="y Label:", font=("Arial", 12), bg="#e6e6fa")
    ylabel_label.grid(row=4, column=0, sticky="w", pady=(5, 5))

    ylabel_entry = tk.Entry(res_frame, font=("Arial", 12), width=35)
    ylabel_entry.grid(row=4, column=1, columnspan=3, pady=(5, 10), padx=(10, 0))



# Run GUI
    root.mainloop()



def csv_upload(status_label, output_box, x_dropdown, y_dropdown, x_var, y_var):
    file_path = filedialog.askopenfilename(
        title = "Select CSV File",
        filetypes=[("CSV Files","*.csv")]
    )
    if file_path:
        try:
            filename = os.path.basename(file_path)
            status_label.config(text=f"File selected: {filename}", fg="green")
            global data
            data = pd.read_csv(file_path)
            headers = data.columns.tolist()

        # updating dropdown menus
            # clear existing menu if new csv is selected
            x_menu = x_dropdown["menu"]
            y_menu = y_dropdown["menu"]
            x_menu.delete(0, "end")
            y_menu.delete(0, "end")

            # set default dropdown option
            x_menu.add_command(label="-", command=lambda: x_var.set("-"))
            y_menu.add_command(label="-", command=lambda: y_var.set("-"))

            # add headers to dropdown

            for col in headers:
                x_menu.add_command(label=col, command=lambda value=col: x_var.set(value))
                y_menu.add_command(label=col, command=lambda value=col: y_var.set(value))

        # clear box if new csv is selected
            output_box.delete("1.0", tk.END) 
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

def handle_plot(x_var, y_var, xres_entry, yres_entry):
    global data
    if data is None:
        print("No file selected")
        return
    
    x_col = x_var.get()
    y_col = y_var.get()

    if x_col == "" or x_col == "-" or y_col == "" or y_col =="-":
        print("Please select variables")
        return
    
    try:
        x_data = data[x_col]
        y_data = data[y_col]

        x_res = int(xres_entry.get())
        y_res = int(yres_entry.get())

        plot = Plotter(x_res, y_res)
        plot.bar_plot(x_data, y_data)

    except Exception as e:
        print (f"Error generating plot: {e}")

if __name__ == "__main__":
    main()