import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
from Plotter import PlotManager

class CSVPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Plotter")
        self.root.geometry("1000x600")
        self.root.configure(bg="#e6e6fa")

        self.df = None
        self.columns = []
        self.plotter = PlotManager()
        self.plot_done = False # for updating the analyze button

        self.create_widgets()

    def create_widgets(self):
        # Title label
        label = tk.Label(self.root, text="CSV Plotter", font=("Helvetica", 18, "bold"), bg="#e6e6fa", fg="black")
        label.pack(pady=(30, 10))

        # Horizontal line divider
        H_line = tk.Frame(self.root, height=2, width=850, bg="black")
        H_line.pack(pady=(0, 30))

        # Upload section
        button_frame = tk.Frame(self.root, bg="#e6e6fa")
        button_frame.pack(anchor="w", padx=140)

        upload_button = tk.Button(button_frame, text="Upload", font=("Arial", 12), command=self.csv_upload)
        upload_button.pack(side="left", padx=10)

        self.status_label = tk.Label(button_frame, text="Please upload a CSV file", font=("Arial", 12), bg="#e6e6fa", fg="black")
        self.status_label.pack(side="left", padx=10)

        # Content Frame
        content_frame = tk.Frame(self.root, bg="#e6e6fa")
        content_frame.pack(padx=140, pady=(10, 0), anchor="nw")

        # Output Box
        output_frame = tk.Frame(content_frame, bg="#e6e6fa")
        output_frame.pack(side="left", fill="both", expand=True)

        yscroll = tk.Scrollbar(output_frame, orient="vertical")
        yscroll.pack(side="right", fill="y")
        xscroll = tk.Scrollbar(output_frame, orient="horizontal")
        xscroll.pack(side="bottom", fill="x")

        self.output_box = tk.Text(output_frame, width=30, height=20, font=("Arial", 12),
                                  yscrollcommand=yscroll.set, xscrollcommand=xscroll.set, wrap="none")
        self.output_box.pack(side="left", fill="both", expand=True)
        yscroll.config(command=self.output_box.yview)
        xscroll.config(command=self.output_box.xview)

        # Right-side controls
        controls_frame = tk.Frame(content_frame, bg="#e6e6fa")
        controls_frame.pack(side="left", padx=(20, 0), anchor="n")

        # Plot type dropdown
        plot_type_label = tk.Label(controls_frame, text="Select plot type:", font=("Arial", 12), bg="#e6e6fa")
        plot_type_label.grid(row=0, column=0, sticky="w")

        self.plot_type_combo = ttk.Combobox(controls_frame, state="disabled", font=("Arial", 12),
                                            values=["Bar", "Scatter", "Line", "Pie Chart", "Heat Map", "Violin Plot", "Box Plot", "Histogram"])
        self.plot_type_combo.grid(row=0, column=1, pady=5)
        self.plot_type_combo.bind("<<ComboboxSelected>>", self.update_column_selection)

        # First column dropdown
        column1_label = tk.Label(controls_frame, text="Select first column:", font=("Arial", 12), bg="#e6e6fa")
        column1_label.grid(row=1, column=0, sticky="w")

        self.column1_combo = ttk.Combobox(controls_frame, state="disabled", font=("Arial", 12))
        self.column1_combo.grid(row=1, column=1, pady=5)

        # Second column dropdown
        column2_label = tk.Label(controls_frame, text="Select second column:", font=("Arial", 12), bg="#e6e6fa")
        column2_label.grid(row=2, column=0, sticky="w")

        self.column2_combo = ttk.Combobox(controls_frame, state="disabled", font=("Arial", 12))
        self.column2_combo.grid(row=2, column=1, pady=5)

        # Resolution entries
        res_label = tk.Label(controls_frame, text="Resolution:", font=("Arial", 12), bg="#e6e6fa")
        res_label.grid(row=3, column=0, sticky="w", pady=(20, 5))

        res_frame = tk.Frame(controls_frame, bg="#e6e6fa")
        res_frame.grid(row=3, column=1, pady=(20, 5), sticky="w")

        self.xres_entry = tk.Entry(res_frame, font=("Arial", 12), width=8)
        self.xres_entry.insert(0, "1280")
        self.xres_entry.pack(side="left")

        x_label = tk.Label(res_frame, text="x", font=("Arial", 12), bg="#e6e6fa")
        x_label.pack(side="left", padx=(5, 5))

        self.yres_entry = tk.Entry(res_frame, font=("Arial", 12), width=8)
        self.yres_entry.insert(0, "720")
        self.yres_entry.pack(side="left")

        # Custom title and label

        # Title
        title_label = tk.Label(controls_frame, text="Title:", font=("Arial", 12), bg="#e6e6fa")
        title_label.grid(row=4, column=0, sticky="w")
        self.title_entry = tk.Entry(controls_frame, font=("Arial", 12), width=30)
        self.title_entry.grid(row=4, column=1, pady=5)

        # x label
        xlabel_label = tk.Label(controls_frame, text="X Label:", font=("Arial", 12), bg="#e6e6fa")
        xlabel_label.grid(row=5, column=0, sticky="w")
        self.xlabel_entry = tk.Entry(controls_frame, font=("Arial", 12), width=30)
        self.xlabel_entry.grid(row=5, column=1, pady=5)

        # y label
        ylabel_label = tk.Label(controls_frame, text="Y Label:", font=("Arial", 12), bg="#e6e6fa")
        ylabel_label.grid(row=6, column=0, sticky="w")
        self.ylabel_entry = tk.Entry(controls_frame, font=("Arial", 12), width=30)
        self.ylabel_entry.grid(row=6, column=1, pady=5)


        # Plot & analyze buttons
        button_row = tk.Frame(controls_frame, bg="#e6e6fa")
        button_row.grid(row=7, column=0, columnspan=2, pady=20)

        self.plot_button = tk.Button(button_row, text="Plot", font=("Arial", 12), state="disabled", command=self.plot_graph, width = 10)
        self.plot_button.pack(side="left", padx=5)

        self.analyze_button = tk.Button(button_row, text="Analyze", font=("Arial", 12), state="disabled", command=self.analyze_data, width = 10)
        self.analyze_button.pack(side="left", padx=30)

    def csv_upload(self):
        file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                filename = os.path.basename(file_path)
                self.status_label.config(text=f"File selected: {filename}", fg="green")
                self.df = pd.read_csv(file_path)
                self.columns = list(self.df.columns)

                self.plot_type_combo.config(state="readonly")
                
                
                # separation and display of numerical vs string variables
                self.output_box.delete("1.0", tk.END)
                self.output_box.insert(tk.END, "\n  Numerical Variables:\n\n")
                for col in self.columns:
                    if pd.api.types.is_numeric_dtype(self.df[col]):
                        self.output_box.insert(tk.END, f"  -  {col}\n")

                self.output_box.insert(tk.END, "\n  Categorical Variables:\n\n")
                for col in self.columns:
                    if pd.api.types.is_string_dtype(self.df[col]) or pd.api.types.is_object_dtype(self.df[col]):
                        self.output_box.insert(tk.END, f"  -  {col}\n")

            except Exception as e:
                self.status_label.config(text="Error reading file, please check CSV", fg="red")
                self.output_box.delete("1.0", tk.END)
                self.output_box.insert(tk.END, str(e))
        else:
            self.status_label.config(text="Please upload a CSV file", fg="black")

    def update_column_selection(self, event):
        plot_type = self.plot_type_combo.get()
        self.column1_combo['values'] = self.columns
        self.column2_combo['values'] = self.columns

        if plot_type in ["Pie Chart", "Histogram"]:
            self.column1_combo.config(state="normal")
            self.column2_combo.config(state="disabled")
        elif plot_type == "Heat Map":
            self.column1_combo.config(state="disabled")
            self.column2_combo.config(state="disabled")
        else:
            self.column1_combo.config(state="normal")
            self.column2_combo.config(state="normal")

        self.column1_combo.set("")
        self.column2_combo.set("")
        self.plot_button.config(state="normal")
        self.analyze_button.config(state="disabled")

    def plot_graph(self):
        plot_type = self.plot_type_combo.get()
        col1 = self.column1_combo.get()
        col2 = self.column2_combo.get()

        if plot_type in ["Bar", "Scatter", "Line", "Violin Plot", "Box Plot"] and (
                col1 not in self.df.columns or col2 not in self.df.columns):
            messagebox.showerror("Error", "Invalid columns selected!")
            return
        elif plot_type in ["Pie Chart", "Histogram"] and col1 not in self.df.columns:
            messagebox.showerror("Error", "Invalid column selected!")
            return

        try:
            xres = int(self.xres_entry.get())
            yres = int(self.yres_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid resolution values!")
            return
        

        title = self.title_entry.get()
        xlabel = self.xlabel_entry.get()
        ylabel = self.ylabel_entry.get()

        self.plotter.plot(self.df, plot_type, col1 if col1 else None, col2 if col2 else None, xres, yres, title=title, xlabel=xlabel, ylabel=ylabel)

        self.plot_done = True # this is for updating the analyze button 
        self.analyze_button.config(state="normal")


    def analyze_data(self):
            plot_type = self.plot_type_combo.get()
            col1 = self.column1_combo.get()
            col2 = self.column2_combo.get()

            if col1 and col2 and plot_type not in ["Pie Chart", "Heat Map", "Histogram"]:
                self.plotter.perform_stat_test(self.df, col1, col2)
            else:
                messagebox.showinfo("Analysis", "Statistical analysis is not applicable for this plot type.")