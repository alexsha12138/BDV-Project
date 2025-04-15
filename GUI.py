import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
from Plotter import PlotManager

class CSVPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Plotter")
        self.root.geometry("1000x650")
        self.root.configure(bg="#f0f0f0")

        self.df = None
        self.columns = []
        self.plotter = PlotManager()
        self.plot_done = False # for updating the analyze button

        self.create_widgets()

    def create_widgets(self):

        # Title label
        label = tk.Label(self.root, text="CSV Plotter", font=("Helvetica", 18, "bold"), bg="#f0f0f0", fg="black")
        label.pack(pady=(30, 10))

        # Horizontal line divider
        H_line = tk.Frame(self.root, height=2, width=850, bg="black")
        H_line.pack(pady=(0, 30))

        # Upload section
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(anchor="w", padx=140)

        upload_button = tk.Button(button_frame, text="Upload", font=("Arial", 12), command=self.csv_upload)
        upload_button.pack(side="left", padx=10)

        self.status_label = tk.Label(button_frame, text="Please upload a CSV file", font=("Arial", 12), bg="#f0f0f0", fg="black")
        self.status_label.pack(side="left", padx=10)

        # Content Frame
        content_frame = tk.Frame(self.root, bg="#f0f0f0")
        content_frame.pack(padx=140, pady=(10, 0), anchor="nw")

        # Output Frames for variables
        output_frame = tk.Frame(content_frame, bg="#f0f0f0")
        output_frame.pack(side="left", fill="y")

        # Numerical Variables Frame
        self.num_frame = tk.LabelFrame(output_frame, text="Numerical Variables", font=("Arial", 12, "bold"), bg="#f0f0f0", bd=0, highlightthickness=0)
        self.num_frame.pack(fill="both", expand=True, pady=(0, 10))
        self.num_listbox = tk.Listbox(self.num_frame, width=30, height=10, font=("Arial", 12))
        self.num_listbox.pack(side="left", fill="both", expand=True)
        num_scroll = tk.Scrollbar(self.num_frame, orient="vertical", command=self.num_listbox.yview)
        num_scroll.pack(side="right", fill="y")
        self.num_listbox.config(yscrollcommand=num_scroll.set)

        # Categorical Variables Frame
        self.cat_frame = tk.LabelFrame(output_frame, text="Categorical Variables", font=("Arial", 12, "bold"), bg="#f0f0f0", bd=0, highlightthickness=0)
        self.cat_frame.pack(fill="both", expand=True)
        self.cat_listbox = tk.Listbox(self.cat_frame, width=30, height=10, font=("Arial", 12))
        self.cat_listbox.pack(side="left", fill="both", expand=True)
        cat_scroll = tk.Scrollbar(self.cat_frame, orient="vertical", command=self.cat_listbox.yview)
        cat_scroll.pack(side="right", fill="y")
        self.cat_listbox.config(yscrollcommand=cat_scroll.set)

        # Right-side controls
        controls_frame = tk.Frame(content_frame, bg="#f0f0f0")
        controls_frame.pack(side="left", padx=(20, 0), anchor="center")


        # First column dropdown
        column1_label = tk.Label(controls_frame, text="Select first variable:", font=("Arial", 12), bg="#f0f0f0")
        column1_label.grid(row=0, column=0, sticky="w")

        self.column1_combo = ttk.Combobox(controls_frame, state="disabled", font=("Arial", 12))
        self.column1_combo.grid(row=0, column=1, pady=5)
        self.column1_combo.bind("<<ComboboxSelected>>", self.update_plot_selection) 

        # Second column dropdown
        column2_label = tk.Label(controls_frame, text="Select second variable:", font=("Arial", 12), bg="#f0f0f0")
        column2_label.grid(row=1, column=0, sticky="w")

        self.column2_combo = ttk.Combobox(controls_frame, state="disabled", font=("Arial", 12))
        self.column2_combo.grid(row=1, column=1, pady=5)
        self.column2_combo.bind("<<ComboboxSelected>>", self.update_plot_selection) 

        # Plot type dropdown
        plot_type_label = tk.Label(controls_frame, text="Select plot type:", font=("Arial", 12), bg="#f0f0f0")
        plot_type_label.grid(row=2, column=0, sticky="w")

        self.plot_type_combo = ttk.Combobox(controls_frame, state="disabled", font=("Arial", 12),
                                            values=["Bar", "Scatter", "Line", "Pie Chart", "Heat Map", "Violin Plot", "Box Plot", "Histogram"])
        self.plot_type_combo.grid(row=2, column=1, pady=5)
        self.plot_type_combo.bind("<<ComboboxSelected>>", self.plot_type_selected)


        # Resolution entries
        res_label = tk.Label(controls_frame, text="Resolution:", font=("Arial", 12), bg="#f0f0f0")
        res_label.grid(row=3, column=0, sticky="w", pady=(20, 5))

        res_frame = tk.Frame(controls_frame, bg="#f0f0f0")
        res_frame.grid(row=3, column=1, pady=(20, 5), sticky="w")

        self.xres_entry = tk.Entry(res_frame, font=("Arial", 12), width=8)
        self.xres_entry.insert(0, "1280")
        self.xres_entry.pack(side="left")

        x_label = tk.Label(res_frame, text="x", font=("Arial", 12), bg="#f0f0f0")
        x_label.pack(side="left", padx=(5, 5))

        self.yres_entry = tk.Entry(res_frame, font=("Arial", 12), width=8)
        self.yres_entry.insert(0, "720")
        self.yres_entry.pack(side="left")

        # Custom title and label

        # Title
        title_label = tk.Label(controls_frame, text="Title:", font=("Arial", 12), bg="#f0f0f0")
        title_label.grid(row=4, column=0, sticky="w")
        self.title_entry = tk.Entry(controls_frame, font=("Arial", 12), width=30)
        self.title_entry.grid(row=4, column=1, pady=5)

        # x label
        xlabel_label = tk.Label(controls_frame, text="X Label:", font=("Arial", 12), bg="#f0f0f0")
        xlabel_label.grid(row=5, column=0, sticky="w")
        self.xlabel_entry = tk.Entry(controls_frame, font=("Arial", 12), width=30)
        self.xlabel_entry.grid(row=5, column=1, pady=5)

        # y label
        ylabel_label = tk.Label(controls_frame, text="Y Label:", font=("Arial", 12), bg="#f0f0f0")
        ylabel_label.grid(row=6, column=0, sticky="w")
        self.ylabel_entry = tk.Entry(controls_frame, font=("Arial", 12), width=30)
        self.ylabel_entry.grid(row=6, column=1, pady=5)


        # Plot & analyze buttons
        button_row = tk.Frame(controls_frame, bg="#f0f0f0")
        button_row.grid(row=7, column=0, columnspan=2, pady=20)

        self.plot_button = tk.Button(button_row, text="Plot", font=("Arial", 12), state="disabled", command=self.plot_graph, width = 10)
        self.plot_button.pack(side="left", padx=5)

        self.analyze_button = tk.Button(button_row, text="Analyze", font=("Arial", 12), state="disabled", command=self.analyze_data, width = 10)
        self.analyze_button.pack(side="left", padx=30)

        # Advanced setting button
        self.advanced_button = tk.Button(button_row, text="Advanced..", font=("Arial", 12), state="disabled", width=10, command=self.advanced_setting)
        self.advanced_button.pack (side = "left", padx=30)

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

                self.num_listbox.delete(0, tk.END) # clear boxes if new file is selected
                self.cat_listbox.delete(0, tk.END)

                # create lists to store numerical vs categorical variable names
                self.numeric_columns = [col for col in self.columns if pd.api.types.is_numeric_dtype(self.df[col])]
                self.categorical_columns = [col for col in self.columns if pd.api.types.is_string_dtype(self.df[col]) or pd.api.types.is_object_dtype(self.df[col])]

                # reset dropdown options when new file is uploaded
                self.plot_type_combo.set("")
                self.column1_combo.set("")
                self.column2_combo.set("")

                self.column1_combo.config(state="readonly")
                self.column2_combo.config(state="readonly")
                self.plot_type_combo.config(state="disabled")

                values = [""] +self.numeric_columns + self.categorical_columns
                self.column1_combo['values'] = values
                self.column2_combo['values'] = values

                self.plot_button.config(state="disabled")
                self.analyze_button.config(state="disabled")

                for col in self.numeric_columns:
                    self.num_listbox.insert(tk.END, col)
                for col in self.categorical_columns:
                    self.cat_listbox.insert(tk.END, col)
            except Exception as e:
                self.status_label.config(text="Error reading file, please check CSV", fg="red")
                self.output_box.delete("1.0", tk.END)
                self.output_box.insert(tk.END, str(e))
        else:
            self.status_label.config(text="Please upload a CSV file", fg="black")


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

    def advanced_setting(self):
        adv_window = tk.Toplevel(self.root)
        adv_window.title("Advanced Settings")
        adv_window.configure(bg="#f0f0f0")

        label=tk.Label(adv_window, text="       Advanced Settings       ", font=("Arial", 16), bg="#f0f0f0")
        label.pack(pady=0)

        col1 = self.column1_combo.get()
        col2 = self.column2_combo.get()

        if self.plot_type_combo.get() == "Line":
            Line_label = tk.Label(adv_window, text="Line Graph", font=("Arial", 12), bg="#f0f0f0")
            Line_label.pack(pady=0)

            # marker
            marker_var = tk.BooleanVar()
            marker_checkbox = tk.Checkbutton(adv_window, text = "Show Marker", variable = marker_var, font=("Arial", 12))
            marker_checkbox.pack(pady=10)

        # advanced menu for bar plot with 2 numerical variables
        elif self.plot_type_combo.get() == "Bar" and col1 in self.numeric_columns and col2 in self.numeric_columns:
            Line_label = tk.Label(adv_window, text="Bar Graph", font=("Arial", 12), bg="#f0f0f0")
            Line_label.pack(pady=0)

            # check box for 1 sample t-test
            t1_marker_var = tk.BooleanVar(value=self.plotter.t1_bool)
            t1_marker_checkbox = tk.Checkbutton(adv_window, text = "Plot 1 sample t-test", variable = t1_marker_var, font=("Arial", 12))
            t1_marker_checkbox.pack(pady=10)

            # reference values for 1 sample t-test
            t1_col1_ref_lab = tk.Label(adv_window, text = "Variable 1 reference value:",font=("Arial", 12), bg="#f0f0f0")
            t1_col1_ref_lab.pack(pady=0)
            t1_col1_ref_entry = tk.Entry(adv_window, font=("Arial", 12), width=10)
            t1_col1_ref_entry.pack(pady=10)
            t1_col1_ref_entry.insert(0, str(self.plotter.t1_ref1))
            
            t1_col2_ref_lab = tk.Label(adv_window, text = "Variable 2 reference value:",font=("Arial", 12), bg="#f0f0f0")
            t1_col2_ref_lab.pack(pady=0)
            t1_col2_ref_entry = tk.Entry(adv_window, font=("Arial", 12), width=10)
            t1_col2_ref_entry.pack(pady=10)
            t1_col2_ref_entry.insert(0, str(self.plotter.t1_ref2))

            # check box for 2 sample t-test
            t2_marker_var = tk.BooleanVar(value=self.plotter.t2_bool)
            t2_marker_checkbox = tk.Checkbutton(adv_window, text = "Plot 2 sample t-test", variable = t2_marker_var, font=("Arial", 12))
            t2_marker_checkbox.pack(pady=10)
            '''
            def save_advanced_settings():
                self.plotter.t1_bool = t1_marker_var.get()
                self.plotter.t2_bool = t2_marker_var.get()

                # ensures entries are numbers, or else default to 0
                try:
                    self.plotter.t1_ref1 = float(t1_col1_ref_entry.get())
                except ValueError:
                    self.plotter.t1_ref1 = 0
                try:
                    self.plotter.t1_ref2 = float(t1_col2_ref_entry.get())
                except ValueError:
                    self.plotter.t1_ref2 = 0
                messagebox.showinfo("Settings Saved", "Advanced settings saved successfully!")
            '''
            save_button = tk.Button(
                                    adv_window,
                                    text="Save",
                                    font=("Arial", 12),
                                    command=lambda: self.save_advanced_settings({
                                        't1_bool': (t1_marker_var, bool),
                                    't2_bool': (t2_marker_var, bool),
                                    't1_ref1': (t1_col1_ref_entry, float),
                                    't1_ref2': (t1_col2_ref_entry, float),
                                })
                            )
            save_button.pack(pady=(20, 10))


        #options for scatterplot
        elif self.plot_type_combo.get() == "Scatter":
            Line_label = tk.Label(adv_window, text="Scatter Plot", font=("Arial", 12), bg="#f0f0f0")
            Line_label.pack(pady=0)

            best_fit_var = tk.BooleanVar(value=True) 
            best_fit_checkbox = tk.Checkbutton(adv_window, text="Show Line of Best Fit", variable=best_fit_var, font=("Arial", 12))
            best_fit_checkbox.pack(pady=10)
            

            def save_scatter_settings():
                self.plotter.show_best_fit = best_fit_var.get()
                messagebox.showinfo("Settings Saved", "Scatter plot settings saved successfully!")

            save_button = tk.Button(adv_window, text="Save", font=("Arial", 12), command=save_scatter_settings)
            save_button.pack(pady=(20, 10))

        # advanced menu for bar plot with 2 numerical variables
        elif self.plot_type_combo.get() == "Bar" and col1 in self.categorical_columns and col2 in self.numeric_columns:
            Line_label = tk.Label(adv_window, text="Bar Graph", font=("Arial", 12), bg="#f0f0f0")
            Line_label.pack(pady=0)

            # Entry box for input category names
            input_cat_label = tk.Label(adv_window, text = "Input Group (separated by \",\"): ")
            input_cat_label.pack(pady=10)
            input_cat_entry = tk.Entry(adv_window, font = ("Arial", 12), width=20)
            input_cat_entry.pack(pady=10)
            input_cat_entry.insert(0, self.plotter.input_cat)

            # Checkbox for Anova
            anova_var = tk.BooleanVar(value=self.plotter.t1_bool)
            anova_checkbox = tk.Checkbutton(adv_window, text = "Perform ANOVA", variable = anova_var, font=("Arial", 12))
            anova_checkbox.pack(pady=10)
            

            save_button = tk.Button(
                                    adv_window,
                                    text="Save",
                                    font=("Arial", 12),
                                    command=lambda: self.save_advanced_settings({
                                        'input_cat': (input_cat_entry, str),
                                        'anova': (anova_var, bool)
                                    })
                                )

            save_button.pack(pady=(20, 10))
        
        elif self.plot_type_combo.get() == "Pie Chart":
            Pie_label = tk.Label(adv_window, text="Pie Chart", font=("Arial", 12), bg="#f0f0f0")
            Pie_label.pack(pady=0)

            # Display Option Dropdown
            display_label = tk.Label(adv_window, text="Display beside pie sections:", font=("Arial", 12), bg="#f0f0f0")
            display_label.pack(pady=(10, 0))

            display_var = tk.StringVar(value=self.plotter.pie_display_option if hasattr(self.plotter, "pie_display_option") else "count")
            display_dropdown = ttk.Combobox(adv_window, textvariable=display_var, font=("Arial", 12), state="readonly")
            display_dropdown['values'] = ["count", "percentage", "both", "neither"]
            display_dropdown.pack(pady=5)

            # Labels Toggle
            labels_var = tk.BooleanVar(value=self.plotter.pie_show_labels if hasattr(self.plotter, "pie_show_labels") else True)
            labels_checkbox = tk.Checkbutton(adv_window, text="Show Labels", variable=labels_var, font=("Arial", 12), bg="#f0f0f0")
            labels_checkbox.pack(pady=5)

            # Legend Toggle
            legend_var = tk.BooleanVar(value=self.plotter.pie_show_legend if hasattr(self.plotter, "pie_show_legend") else True)
            legend_checkbox = tk.Checkbutton(adv_window, text="Show Legend", variable=legend_var, font=("Arial", 12), bg="#f0f0f0")
            legend_checkbox.pack(pady=5)

            # Save Button
            save_button = tk.Button(
                adv_window,
                text="Save",
                font=("Arial", 12),
                command=lambda: self.save_advanced_settings({
                    'pie_display_option': (display_var, str),
                    'pie_show_labels': (labels_var, bool),
                    'pie_show_legend': (legend_var, bool),
                }, confirmation_text="Pie chart settings saved.")
            )
            save_button.pack(pady=(20, 10))
    
    
    def save_advanced_settings(self, widget_map, confirmation_text="Advanced settings saved successfully!"):
        for attr, (widget, cast) in widget_map.items():
            try:
                setattr(self.plotter, attr, cast(widget.get()))
            except Exception:
                setattr(self.plotter, attr, 0 if cast == float else False if cast == bool else "")
        messagebox.showinfo("Settings Saved", confirmation_text)



    def update_plot_selection(self, event):
        col1 = self.column1_combo.get()
        col2 = self.column2_combo.get()
        if col1:
            self.plot_type_combo.config(state="readonly")

            # Update plot type options based on new Column 1
            self.plot_type_combo.set("")
            
            if col1 in self.numeric_columns and col2 =="":
                self.plot_type_combo["values"] = [""]
            elif col1 in self.numeric_columns and col2 in self.categorical_columns:
                self.plot_type_combo["values"] = [""]
            elif col1 in self.categorical_columns and col2 in self.numeric_columns:
                self.plot_type_combo["values"] = ["Bar", "Violin Plot", "Box Plot"]
            elif col1 in self.numeric_columns and col2 in self.numeric_columns:
                self.plot_type_combo["values"] = ["Scatter", "Line", "Histogram", "Bar", "Violin Plot", "Box Plot"]
            elif col1 in self.categorical_columns and col2 == "":
                self.plot_type_combo["values"] = ["Pie Chart"]
            elif col1 in self.categorical_columns and col2 in self.categorical_columns:
                self.plot_type_combo["values"] = ["Heat Map"]

    def plot_type_selected(self, event):
        plot_type = self.plot_type_combo.get()
        col1 = self.column1_combo.get()
        col2 = self.column2_combo.get()

        # Only enable if a plot type is selected
        if plot_type != "":
            self.plot_button.config(state="normal")
            self.advanced_button.config(state="normal")
            self.analyze_button.config(state="normal")

        else:
            self.plot_button.config(state="disabled")
            self.analyze_button.config(state="disabled")