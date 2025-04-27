import tkinter as tk
from tkinter import colorchooser
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
from Plotter import PlotManager
from scipy.stats import linregress
import scipy.stats as stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd


class CSVPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Plotter")
        self.root.geometry("1000x650")
        self.root.configure(bg="#f0f0f0")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", background="#f0f0f0", foreground="black")
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TCombobox", fieldbackground="white", background="white", foreground="black")
        style.configure("TEntry", fieldbackground="white", background="white", foreground="black")

        style.map("TCombobox",
            fieldbackground=[
                ("disabled", "#d9d9d9"),   # Light gray when disabled
                ("readonly", "white")      # White when selection is made
            ],
            background=[
                ("disabled", "#d9d9d9"),   # Light gray border when disabled
                ("readonly", "white")      # White background otherwise
            ],
            foreground=[
                ("disabled", "gray"),      # Gray text when disabled
                ("readonly", "black")      # Black text when selected
            ]
        )

        self.df = None
        self.columns = []
        self.plotter = PlotManager()
        self.plot_done = False  # for updating the analyze button

        self.create_widgets()
        # Initialize heatmap color variables
        self.plotter.heatmap_low_color = "#FFFFFF"  # white
        self.plotter.heatmap_high_color = "#0000FF"  # blue

        # Initialize line graph color variables
        self.plotter.line_color = "#1f77b4"  # Default blue
        self.plotter.marker_color = "#ff7f0e"  # Default orange

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

        self.status_label = tk.Label(button_frame, text="Please upload a CSV file", font=("Arial", 12), bg="#f0f0f0",
                                     fg="black")
        self.status_label.pack(side="left", padx=10)

        # Content Frame
        content_frame = tk.Frame(self.root, bg="#f0f0f0")
        content_frame.pack(padx=140, pady=(10, 0), anchor="nw")

        # Output Frames for variables
        output_frame = tk.Frame(content_frame, bg="#f0f0f0")
        output_frame.pack(side="left", fill="y")

        # Numerical Variables Frame
        self.num_frame = tk.LabelFrame(output_frame, text="Numerical Variables", font=("Arial", 12, "bold"),
                                       bg="#f0f0f0", fg="black", bd=0, highlightthickness=0)
        self.num_frame.pack(fill="both", expand=True, pady=(0, 10))
        self.num_listbox = tk.Listbox(self.num_frame, width=30, height=10, font=("Arial", 12), bg="white", fg="black")
        self.num_listbox.pack(side="left", fill="both", expand=True)
        num_scroll = tk.Scrollbar(self.num_frame, orient="vertical", command=self.num_listbox.yview)
        num_scroll.pack(side="right", fill="y")
        self.num_listbox.config(yscrollcommand=num_scroll.set)

        # Categorical Variables Frame
        self.cat_frame = tk.LabelFrame(output_frame, text="Categorical Variables", font=("Arial", 12, "bold"),
                                       bg="#f0f0f0", fg="black", bd=0, highlightthickness=0)
        self.cat_frame.pack(fill="both", expand=True)
        self.cat_listbox = tk.Listbox(self.cat_frame, width=30, height=10, font=("Arial", 12), bg="white", fg="black")
        self.cat_listbox.pack(side="left", fill="both", expand=True)
        cat_scroll = tk.Scrollbar(self.cat_frame, orient="vertical", command=self.cat_listbox.yview)
        cat_scroll.pack(side="right", fill="y")
        self.cat_listbox.config(yscrollcommand=cat_scroll.set)

        # Right-side controls
        controls_frame = tk.Frame(content_frame, bg="#f0f0f0")
        controls_frame.pack(side="left", padx=(20, 0), anchor="center")

        # First column dropdown
        column1_label = tk.Label(controls_frame, text="Select first variable:", font=("Arial", 12), bg="#f0f0f0", fg="black")
        column1_label.grid(row=0, column=0, sticky="w")

        self.column1_combo = ttk.Combobox(controls_frame, state="disabled", font=("Arial", 12))
        self.column1_combo.grid(row=0, column=1, pady=5)
        self.column1_combo.bind("<<ComboboxSelected>>", self.update_plot_selection)

        # Second column dropdown
        column2_label = tk.Label(controls_frame, text="Select second variable:", font=("Arial", 12), bg="#f0f0f0", fg="black")
        column2_label.grid(row=1, column=0, sticky="w")

        self.column2_combo = ttk.Combobox(controls_frame, state="disabled", font=("Arial", 12))
        self.column2_combo.grid(row=1, column=1, pady=5)
        self.column2_combo.bind("<<ComboboxSelected>>", self.update_plot_selection)

        # Third column dropdown
        column3_label = tk.Label(controls_frame, text="Select third variable:", font=("Arial", 12), bg="#f0f0f0", fg="black")
        column3_label.grid(row=2, column=0, sticky="w")

        self.column3_combo = ttk.Combobox(controls_frame, state="disabled", font=("Arial", 12))
        self.column3_combo.grid(row=2, column=1, pady=5)
        self.column3_combo.bind("<<ComboboxSelected>>", self.update_plot_selection)
        
        # Plot type dropdown
        plot_type_label = tk.Label(controls_frame, text="Select plot type:", font=("Arial", 12), bg="#f0f0f0", fg="black")
        plot_type_label.grid(row=3, column=0, sticky="w")

        self.plot_type_combo = ttk.Combobox(controls_frame, state="disabled", font=("Arial", 12),
                                            values=["Heat Map", "Pairplot"])
        self.plot_type_combo.grid(row=3, column=1, pady=5)
        self.plot_type_combo.bind("<<ComboboxSelected>>", self.plot_type_selected)

        #HEATMAP (from lines 116-152)
        # Add color selection frame for heatmap
        self.color_selection_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.color_selection_frame.pack_forget()  # Hidden by default

        # Low color selection
        self.low_color_button = tk.Button(
            self.color_selection_frame,
            text="Select Low Color",
            command=lambda: self.select_color('low'),
            font=("Arial", 10)
        )
        self.low_color_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.low_color_display = tk.Label(
            self.color_selection_frame,
            width=5,
            bg=self.plotter.heatmap_low_color,
            relief=tk.RAISED
        )
        self.low_color_display.pack(side=tk.LEFT, padx=5, pady=5)

        # High color selection
        self.high_color_button = tk.Button(
            self.color_selection_frame,
            text="Select High Color",
            command=lambda: self.select_color('high'),
            font=("Arial", 10)
        )
        self.high_color_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.high_color_display = tk.Label(
            self.color_selection_frame,
            width=5,
            bg=self.plotter.heatmap_high_color,
            relief=tk.RAISED
        )
        self.high_color_display.pack(side=tk.LEFT, padx=5, pady=5)

        # Add line color selection frame
        self.line_color_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.line_color_frame.pack_forget()  # Hidden by default

        # Line color selection
        self.line_color_button = tk.Button(
            self.line_color_frame,
            text="Select Line Color",
            command=lambda: self.select_line_color('line'),
            font=("Arial", 10)
        )
        self.line_color_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.line_color_display = tk.Label(
            self.line_color_frame,
            width=5,
            bg=self.plotter.line_color,
            relief=tk.RAISED
        )
        self.line_color_display.pack(side=tk.LEFT, padx=5, pady=5)

        # Marker color selection
        self.marker_color_button = tk.Button(
            self.line_color_frame,
            text="Select Marker Color",
            command=lambda: self.select_line_color('marker'),
            font=("Arial", 10)
        )
        self.marker_color_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.marker_color_display = tk.Label(
            self.line_color_frame,
            width=5,
            bg=self.plotter.marker_color,
            relief=tk.RAISED
        )
        self.marker_color_display.pack(side=tk.LEFT, padx=5, pady=5)

        # Title Font and Text Font Entry Boxes
        font_frame = tk.Frame(controls_frame, bg="#f0f0f0")
        font_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky="w")

        title_font_label = tk.Label(font_frame, text="Title Font:", font=("Arial", 12), bg="#f0f0f0", fg="black", bd=1, highlightthickness=0)
        title_font_label.pack(side="left", padx=(0, 5))
        self.title_font_entry = tk.Entry(font_frame, font=("Arial", 12), width=5, bg="white", fg="black", bd=1, highlightthickness=0)
        self.title_font_entry.insert(0, "14")  # Set default value to 14
        self.title_font_entry.pack(side="left", padx=(0, 10))

        text_font_label = tk.Label(font_frame, text="Text Font:", font=("Arial", 12), bg="#f0f0f0", fg="black", bd=1, highlightthickness=0)
        text_font_label.pack(side="left", padx=(0, 5))
        self.text_font_entry = tk.Entry(font_frame, font=("Arial", 12), width=5, bg="white", fg="black", bd=1, highlightthickness=0)
        self.text_font_entry.insert(0, "12")  # Set default value to 12
        self.text_font_entry.pack(side="left", padx=(0, 5))

        # Graph info Button
        button_row = tk.Frame(controls_frame, bg="#f0f0f0")
        button_row.grid(row=4, column=1, columnspan=2, pady=5, sticky="e")

        self.graph_info = tk.Button(button_row, text="Graph Info", font=("Arial", 12), state="normal", width=10,
            command=self.graph_info)
        self.graph_info.pack(side="right", padx=38)  # Increased padding on the right side

        # Resolution entries
        res_label = tk.Label(controls_frame, text="Resolution:", font=("Arial", 12), bg="#f0f0f0", fg="black")
        res_label.grid(row=5, column=0, sticky="w", pady=(20, 5))

        res_frame = tk.Frame(controls_frame, bg="#f0f0f0")
        res_frame.grid(row=5, column=1, pady=(20, 5), sticky="w")

        self.xres_entry = tk.Entry(res_frame, font=("Arial", 12), width=8, bg="white", fg="black", bd=1, highlightthickness=0)
        self.xres_entry.insert(0, "1280")
        self.xres_entry.pack(side="left")

        x_label = tk.Label(res_frame, text="x", font=("Arial", 12), bg="#f0f0f0", fg="black")
        x_label.pack(side="left", padx=(5, 5))

        self.yres_entry = tk.Entry(res_frame, font=("Arial", 12), width=8, bg="white", fg="black", bd=1, highlightthickness=0)
        self.yres_entry.insert(0, "720")
        self.yres_entry.pack(side="left")

        # Custom title and label
        title_label = tk.Label(controls_frame, text="Title:", font=("Arial", 12), bg="#f0f0f0", fg="black")
        title_label.grid(row=6, column=0, sticky="w")
        self.title_entry = tk.Entry(controls_frame, font=("Arial", 12), width=30, bg="white", fg="black", bd=1, highlightthickness=0)
        self.title_entry.grid(row=6, column=1, pady=5)

        # x label
        xlabel_label = tk.Label(controls_frame, text="X Label:", font=("Arial", 12), bg="#f0f0f0", fg="black")
        xlabel_label.grid(row=7, column=0, sticky="w")
        self.xlabel_entry = tk.Entry(controls_frame, font=("Arial", 12), width=30, bg="white", fg="black", bd=1, highlightthickness=0)
        self.xlabel_entry.grid(row=7, column=1, pady=5)

        # y label
        ylabel_label = tk.Label(controls_frame, text="Y Label:", font=("Arial", 12), bg="#f0f0f0", fg="black")
        ylabel_label.grid(row=8, column=0, sticky="w")
        self.ylabel_entry = tk.Entry(controls_frame, font=("Arial", 12), width=30, bg="white", fg="black", bd=1, highlightthickness=0)
        self.ylabel_entry.grid(row=8, column=1, pady=5)

        # Plot & analyze buttons
        button_row = tk.Frame(controls_frame, bg="#f0f0f0")
        button_row.grid(row=9, column=0, columnspan=2, pady=20)

        self.plot_button = tk.Button(button_row, text="Plot", font=("Arial", 12), state="disabled",
                                     command=self.plot_graph, width=10)
        self.plot_button.pack(side="left", padx=5)

        self.analyze_button = tk.Button(button_row, text="Analyze", font=("Arial", 12), state="disabled",
                                        command=self.analyze_data, width=10)
        self.analyze_button.pack(side="left", padx=30)

        # Advanced setting button
        self.advanced_button = tk.Button(button_row, text="Advanced..", font=("Arial", 12), state="disabled", width=10,
                                         command=self.advanced_setting)
        self.advanced_button.pack(side="left", padx=30)

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
                self.num_listbox.delete(0, tk.END)  # clear boxes if new file is selected
                self.cat_listbox.delete(0, tk.END)

                # create lists to store numerical vs categorical variable names
                self.numeric_columns = [col for col in self.columns if pd.api.types.is_numeric_dtype(self.df[col])]
                self.categorical_columns = [col for col in self.columns if
                                            pd.api.types.is_string_dtype(self.df[col]) or pd.api.types.is_object_dtype(
                                                self.df[col])]

                # reset dropdown options when new file is uploaded
                self.plot_type_combo.set("")
                self.column1_combo.set("")
                self.column2_combo.set("")

                self.column1_combo.config(state="readonly")
                self.column2_combo.config(state="readonly")
                self.plot_type_combo.config(state="readonly")

                values = [""] + self.numeric_columns + self.categorical_columns
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
                messagebox.showerror("Error", str(e))
        else:
            self.status_label.config(text="Please upload a CSV file", fg="black")

    def plot_graph(self):
        plot_type = self.plot_type_combo.get()

        if plot_type == "Pairplot":
            if self.df is None:
                messagebox.showerror("Error", "No dataset loaded!")
                return
            if not self.numeric_columns:
                messagebox.showerror("Error", "No numerical variables available for pairplot!")
                return
            try:
                self.plotter.pairplot(self.df, self.numeric_columns)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create pairplot: {str(e)}")
            return

        # Existing logic for other plot types
        col1 = self.column1_combo.get()
        col2 = self.column2_combo.get()
        col3 = self.column3_combo.get()

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
            messagebox.showerror("Error", "Invalid resolution value(s)!")
            return
        
        try:
            title_font = int(self.title_font_entry.get())
            text_font = int(self.text_font_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid font size value(s)!")
            return
        

        title = self.title_entry.get()
        xlabel = self.xlabel_entry.get()
        ylabel = self.ylabel_entry.get()

        self.plotter.plot(self.df, plot_type, col1 if col1 else None, col2 if col2 else None, col3 if col3 else None,
                          xres, yres, title=title, xlabel=xlabel, ylabel=ylabel, title_font=title_font, text_font=text_font)

        self.plot_done = True  # this is for updating the analyze button
        self.analyze_button.config(state="normal")

    def analyze_data(self):
        plot_type = self.plot_type_combo.get()
        col1 = self.column1_combo.get()
        col2 = self.column2_combo.get()
        col3 = self.column3_combo.get()

        if plot_type == "Scatter" and col1 and col2:
            
            slope, intercept, r_value, p_value, std_err = linregress(self.df[col1], self.df[col2])
            equation = f"y = {slope:.2f}x + {intercept:.2f}"
            messagebox.showinfo("Line of Best Fit", f"Equation: {equation}\nR: {r_value:.2f}\nR²: {r_value ** 2:.2f}")
        
        elif (plot_type == "Bar" or plot_type == "Violin Plot") and col1 in self.numeric_columns and col2 in self.numeric_columns and col3 in self.numeric_columns:            
            
            # Calculate stats
            anova_result = stats.f_oneway(self.df[col1], self.df[col2], self.df[col3])
            p_value_anova = anova_result.pvalue

            # Prepare data for Tukey HSD
            values = pd.concat([self.df[col1], self.df[col2], self.df[col3]], ignore_index=True)
            groups = [col1] * len(self.df[col1]) + [col2] * len(self.df[col2]) + [col3] * len(self.df[col3])
            df_plot = pd.DataFrame({"Value": values, "Group": groups})

            # Tukey HSD
            tukey = pairwise_tukeyhsd(endog=df_plot["Value"], groups=df_plot["Group"], alpha=0.05)

            # Show results in messagebox
            result_str = f"ANOVA p-value: {p_value_anova:.4e}\n\nTukey HSD Summary:\n{tukey.summary().as_text()}"
            messagebox.showinfo("Statistical Results", result_str)


        elif (plot_type == "Bar" or plot_type == "Violin Plot") and col1 in self.numeric_columns and col2 in self.numeric_columns and not col3:
            try:
                # Perform one-sample t-tests
                t_stat1, p_value1 = stats.ttest_1samp(self.df[col1].dropna(), 0)
                t_stat2, p_value2 = stats.ttest_1samp(self.df[col2].dropna(), 0)

                # Perform two-sample t-test
                t_stat_two_sample, p_value_two_sample = stats.ttest_ind(self.df[col1].dropna(), self.df[col2].dropna())

                # Display results
                results = (
                    f"One-Sample T-Test for {col1}:\n"
                    f"  T-Statistic: {t_stat1:.4f}\n"
                    f"  P-Value: {p_value1:.4e}\n\n"
                    f"One-Sample T-Test for {col2}:\n"
                    f"  T-Statistic: {t_stat2:.4f}\n"
                    f"  P-Value: {p_value2:.4e}\n\n"
                    f"Two-Sample T-Test between {col1} and {col2}:\n"
                    f"  T-Statistic: {t_stat_two_sample:.4f}\n"
                    f"  P-Value: {p_value_two_sample:.4e}"
                )
                messagebox.showinfo("T-Test Results", results)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to perform t-tests: {str(e)}")

        elif (plot_type == "Bar" or plot_type == "Violin Plot") and col1 in self.categorical_columns and col2 in self.numeric_columns and not col3:

            if len(self.df[col1].unique()) == 2:
                try:
                    # Perform two-sample t-test for each category in col1
                    categories = self.df[col1].unique()
                    group1 = self.df[self.df[col1] == categories[0]][col2].dropna()
                    group2 = self.df[self.df[col1] == categories[1]][col2].dropna()

                    # Calculate statistics for each group
                    group1_mean = group1.mean()
                    group1_std = group1.std()
                    group2_mean = group2.mean()
                    group2_std = group2.std()

                    # Perform two-sample t-test
                    t_stat, p_value = stats.ttest_ind(group1, group2)

                    # Display results
                    results = (
                        f"T-Test Results for {col1}:\n\n"
                        f"Category: {categories[0]}\n"
                        f"  Mean: {group1_mean:.4f}\n"
                        f"  Standard Deviation: {group1_std:.4f}\n\n"
                        f"Category: {categories[1]}\n"
                        f"  Mean: {group2_mean:.4f}\n"
                        f"  Standard Deviation: {group2_std:.4f}\n\n"
                        f"Two-Sample T-Test:\n"
                        f"  T-Statistic: {t_stat:.4f}\n"
                        f"  P-Value: {p_value:.4e}"
                    )
                    messagebox.showinfo("T-Test Results", results)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to perform t-test: {str(e)}")
            else:
                try:
                    # Perform ANOVA test for multiple categories in col1
                    groups = [self.df[self.df[col1] == category][col2].dropna() for category in self.df[col1].unique()]
                    anova_result = stats.f_oneway(*groups)
                    p_value_anova = anova_result.pvalue

                    # Prepare data for Tukey HSD
                    values = self.df[col2].dropna()
                    groups_labels = self.df[col1][self.df[col2].notna()]
                    tukey = pairwise_tukeyhsd(endog=values, groups=groups_labels, alpha=0.05)

                    # Show results in messagebox
                    result_str = f"ANOVA p-value: {p_value_anova:.4e}\n\nTukey HSD Summary:\n{tukey.summary().as_text()}"
                    messagebox.showinfo("Statistical Results", result_str)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to perform ANOVA: {str(e)}")

        elif plot_type == "Box Plot" and col1 and col2:
            results = []

            # Calculate overall statistics for col2
            overall_data = self.df[col2].dropna()
            overall_minimum = overall_data.min()
            overall_q1 = overall_data.quantile(0.25)
            overall_median = overall_data.median()
            overall_q3 = overall_data.quantile(0.75)
            overall_maximum = overall_data.max()
            overall_iqr = overall_q3 - overall_q1
            overall_lower_bound = overall_q1 - 1.5 * overall_iqr
            overall_upper_bound = overall_q3 + 1.5 * overall_iqr
            overall_non_outliers = overall_data[
                (overall_data >= overall_lower_bound) & (overall_data <= overall_upper_bound)]
            overall_non_outlier_min = overall_non_outliers.min()
            overall_non_outlier_max = overall_non_outliers.max()

            # Append overall statistics
            results.append(
                "Overall Statistics:\n\n"
                f"  Minimum: {overall_minimum:.2f}\n"
                f"  1st Quartile (Q1): {overall_q1:.2f}\n"
                f"  Median: {overall_median:.2f}\n"
                f"  3rd Quartile (Q3): {overall_q3:.2f}\n"
                f"  Maximum: {overall_maximum:.2f}\n"
                f"  IQR: {overall_iqr:.2f}\n"
                f"  Outlier Lower Bound: {overall_lower_bound:.2f}\n"
                f"  Outlier Upper Bound: {overall_upper_bound:.2f}\n"
                f"  Non-Outlier Minimum: {overall_non_outlier_min:.2f}\n"
                f"  Non-Outlier Maximum: {overall_non_outlier_max:.2f}\n"
            )

            # Check if col1 is categorical and col2 is numeric
            if col1 in self.categorical_columns and col2 in self.numeric_columns:
                grouped = self.df.groupby(col1)
                for category, group in grouped:
                    data = group[col2].dropna()  # Drop NaN values for analysis
                    if data.empty:
                        continue

                    # Calculate statistics for each category
                    minimum = data.min()
                    q1 = data.quantile(0.25)
                    median = data.median()
                    q3 = data.quantile(0.75)
                    maximum = data.max()
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    non_outliers = data[(data >= lower_bound) & (data <= upper_bound)]
                    non_outlier_min = non_outliers.min()
                    non_outlier_max = non_outliers.max()

                    # Append results for the category
                    results.append(
                        f"Category: {category}\n\n"
                        f"  Minimum: {minimum:.2f}\n"
                        f"  1st Quartile (Q1): {q1:.2f}\n"
                        f"  Median: {median:.2f}\n"
                        f"  3rd Quartile (Q3): {q3:.2f}\n"
                        f"  Maximum: {maximum:.2f}\n"
                        f"  IQR: {iqr:.2f}\n"
                        f"  Outlier Lower Bound: {lower_bound:.2f}\n"
                        f"  Outlier Upper Bound: {upper_bound:.2f}\n"
                        f"  Non-Outlier Minimum: {non_outlier_min:.2f}\n"
                        f"  Non-Outlier Maximum: {non_outlier_max:.2f}\n"
                    )

            # Display results in a scrollable window
            self.show_scrollable_results("\n\n".join(results))
            return
        # elif col1 and col2 and plot_type in ["Pie Chart", "Heat Map", "Histogram"]:
            ## self.plotter.perform_stat_test(self.df, col1, col2)
        
    
        else:
            messagebox.showinfo("Analysis", "Statistical analysis is unavailable for this plot type.")

    def select_line_color(self, which):
        color = colorchooser.askcolor(title=f"Select {which} color")[1]
        if color:
            if which == 'line':
                self.plotter.line_color = color
                self.line_color_display.config(bg=color)
            else:
                self.plotter.marker_color = color
                self.marker_color_display.config(bg=color)

    def plot_type_selected(self, event):
        plot_type = self.plot_type_combo.get()

        # Show/hide color selection based on plot type
        if plot_type == "Line":
            self.line_color_frame.pack(pady=10)
            self.color_selection_frame.pack_forget()
        elif plot_type == "Heat Map":
            self.color_selection_frame.pack(pady=10)
            self.line_color_frame.pack_forget()
        else:
            self.line_color_frame.pack_forget()
            self.color_selection_frame.pack_forget()

        col1 = self.column1_combo.get()
        col2 = self.column2_combo.get()
        col3 = self.column3_combo.get()

        if plot_type != "":
            self.plot_button.config(state="normal")
            self.advanced_button.config(state="normal")
            self.analyze_button.config(state="normal")
        else:
            self.plot_button.config(state="disabled")
            self.analyze_button.config(state="disabled")

    def advanced_setting(self):
        adv_window = tk.Toplevel(self.root)
        adv_window.title("Advanced Settings")
        adv_window.configure(bg="#f0f0f0")

        label = tk.Label(adv_window, text="       Advanced Settings       ", font=("Arial", 16), bg="#f0f0f0", fg="black")
        label.pack(pady=0)

        col1 = self.column1_combo.get()
        col2 = self.column2_combo.get()
        col3 = self.column3_combo.get()

        if self.plot_type_combo.get() == "Line":
            Line_label = tk.Label(adv_window, text="Line Graph", font=("Arial", 12), bg="#f0f0f0", fg="black")
            Line_label.pack(pady=0)

        # advanced menu for bar plot with 1 categorical and 1 numerical variables
        elif self.plot_type_combo.get() == "Bar" and col1 in self.categorical_columns and col2 in self.numeric_columns:
            Line_label = tk.Label(adv_window, text="Bar Graph", font=("Arial", 12), bg="#f0f0f0", fg="black")
            Line_label.pack(pady=0)

            # Entry box for input category names
            input_cat_label = tk.Label(adv_window, text="Input Group (separated by \",\"): ", font=("Arial", 13), bg="#f0f0f0", fg="black")
            input_cat_label.pack(pady=10)
            input_cat_entry = tk.Entry(adv_window, font=("Arial", 12), width=20, bg="white", fg="black", bd=1, highlightthickness=0)
            input_cat_entry.pack(pady=10)
            input_cat_entry.insert(0, self.plotter.input_cat)

            # Checkbox for Anova
            anova_var = tk.BooleanVar(value=self.plotter.anova_bool)
            anova_checkbox = tk.Checkbutton(adv_window, text="Perform ANOVA/T-Test", variable=anova_var,
                                            font=("Arial", 12), bg="#f0f0f0", fg="black")
            anova_checkbox.pack(pady=10)

            save_button = tk.Button(
                adv_window,
                text="Save",
                font=("Arial", 12),
                command=lambda: self.save_advanced_settings({
                    'input_cat': (input_cat_entry, str),
                    'anova_bool': (anova_var, bool),
                }, window=adv_window)
            )

            save_button.pack(pady=(20, 10))

        # advanced menu for bar plot with 2 numerical variables
        elif self.plot_type_combo.get() == "Bar" and col1 in self.numeric_columns and col2 in self.numeric_columns and col3 == "":
            Line_label = tk.Label(adv_window, text="Bar Graph", font=("Arial", 12), bg="#f0f0f0", fg="black")
            Line_label.pack(pady=0)

            # check box for 1 sample t-test
            t1_marker_var = tk.BooleanVar(value=self.plotter.t1_bool)
            t1_marker_checkbox = tk.Checkbutton(adv_window, text="Plot 1 sample t-test", variable=t1_marker_var,
                                                font=("Arial", 12), bg="#f0f0f0", fg="black")
            t1_marker_checkbox.pack(pady=10)

            # reference values for 1 sample t-test
            t1_col1_ref_lab = tk.Label(adv_window, text="Variable 1 reference value:", font=("Arial", 12), bg="#f0f0f0", fg="black")
            t1_col1_ref_lab.pack(pady=0)
            t1_col1_ref_entry = tk.Entry(adv_window, font=("Arial", 12), width=10, bg="white", fg="black", bd=1, highlightthickness=0)
            t1_col1_ref_entry.pack(pady=10)
            t1_col1_ref_entry.insert(0, str(self.plotter.t1_ref1))

            t1_col2_ref_lab = tk.Label(adv_window, text="Variable 2 reference value:", font=("Arial", 12), bg="#f0f0f0", fg="black")
            t1_col2_ref_lab.pack(pady=0)
            t1_col2_ref_entry = tk.Entry(adv_window, font=("Arial", 12), width=10, bg="white", fg="black", bd=1, highlightthickness=0)
            t1_col2_ref_entry.pack(pady=10)
            t1_col2_ref_entry.insert(0, str(self.plotter.t1_ref2))

            # check box for 2 sample t-test
            t2_marker_var = tk.BooleanVar(value=self.plotter.t2_bool)
            t2_marker_checkbox = tk.Checkbutton(adv_window, text="Plot 2 sample t-test", variable=t2_marker_var,
                                                font=("Arial", 12), bg="#f0f0f0", fg="black")
            t2_marker_checkbox.pack(pady=10)

            save_button = tk.Button(
                adv_window,
                text="Save",
                font=("Arial", 12),
                command=lambda: self.save_advanced_settings({
                    't1_bool': (t1_marker_var, bool),
                    't2_bool': (t2_marker_var, bool),
                    't1_ref1': (t1_col1_ref_entry, float),
                    't1_ref2': (t1_col2_ref_entry, float),
                }, window=adv_window)
            )
            save_button.pack(pady=(20, 10))

        # bar plot with 3 numerical variables
        elif self.plot_type_combo.get() == "Bar" and col1 in self.numeric_columns and col2 in self.numeric_columns and col3 in self.numeric_columns:
            Bar_label = tk.Label(adv_window, text="Bar Graph", font=("Arial", 12), bg="#f0f0f0", fg="black")
            Bar_label.pack(pady=0)
            # check box for anova
            anova_bool = tk.BooleanVar(value=self.plotter.anova_bool)
            anova_bool_checkbox = tk.Checkbutton(adv_window, text="ANOVA test", variable=anova_bool, font=("Arial", 12), bg="#f0f0f0", fg="black")
            anova_bool_checkbox.pack(pady=10)

            save_button = tk.Button(
                adv_window,
                text="Save",
                font=("Arial", 12),
                command=lambda: self.save_advanced_settings({
                    'anova_bool': (anova_bool, bool),
                }, window= adv_window, confirmation_text="Violin plot settings saved.")
            )
            save_button.pack(pady=(20, 10))


        # options for scatterplot
        #3 var scatter
        elif self.plot_type_combo.get() == "Scatter" and col1 in self.numeric_columns and col2 in self.numeric_columns and col3 in self.numeric_columns:
            no_settings_label = tk.Label(adv_window, text="None for this plot", font=("Arial", 12), bg="#f0f0f0", fg="black")
            no_settings_label.pack(pady=20)
        
        #2 var scatter
        elif self.plot_type_combo.get() == "Scatter":
            Line_label = tk.Label(adv_window, text="Scatter Plot", font=("Arial", 12), bg="#f0f0f0", fg="black")
            Line_label.pack(pady=0)

            # Line of Best Fit plot
            best_fit_var = tk.BooleanVar(value=self.plotter.show_best_fit)
            best_fit_checkbox = tk.Checkbutton(adv_window, text="Show Line of Best Fit", variable=best_fit_var,
                                               font=("Arial", 12), bg="#f0f0f0", fg="black")
            best_fit_checkbox = tk.Checkbutton(
                adv_window,
                text="Show Line of Best Fit",
                variable=best_fit_var,
                font=("Arial", 12), bg="#f0f0f0", fg="black",
                command=lambda: toggle_dynamic_checkboxes())
            best_fit_checkbox.pack(pady=10, padx=20, anchor="w")

            def toggle_dynamic_checkboxes():
                # Enable or disable the checkboxes based on the state of "Show Line of Best Fit"
                state = "normal" if best_fit_var.get() else "disabled"
                ci_checkbox.config(state=state)
                equation_checkbox.config(state=state)

            # Checkbox for "Exclude Confidence Interval"
            ci_var = tk.BooleanVar(value=not self.plotter.show_confidence_interval)  # Default to include CI
            ci_checkbox = tk.Checkbutton(
                adv_window,
                text="Exclude Confidence Interval",
                variable=ci_var,
                font=("Arial", 12), bg="#f0f0f0", fg="black",
                state="normal" if best_fit_var.get() else "disabled")  # Enable only if LOBF is selected
            ci_checkbox.pack(pady=10, padx=20, anchor="w")

            # Show Equation for LOBF if LOBF is selected
            equation_var = tk.BooleanVar(value=self.plotter.show_equation)
            equation_checkbox = tk.Checkbutton(
                adv_window,
                text="Show Equation",
                variable=equation_var,
                font=("Arial", 12), bg="#f0f0f0", fg="black",
                state="normal" if best_fit_var.get() else "disabled")
            equation_checkbox.pack(pady=10, padx=20, anchor="w")

            # Show R value
            r_var = tk.BooleanVar(value=self.plotter.show_r)
            r_checkbox = tk.Checkbutton(adv_window, text="Show R (Correlation Coefficient)", variable=r_var,
                                        font=("Arial", 12), bg="#f0f0f0", fg="black", state="normal")
            r_checkbox.pack(pady=10, padx=20, anchor="w")

            # Show R² value
            r2_var = tk.BooleanVar(value=self.plotter.show_r2)
            r2_checkbox = tk.Checkbutton(adv_window, text="Show R² (Coefficient of Determination)", variable=r2_var,
                                         font=("Arial", 12), bg="#f0f0f0", fg="black", state="normal")
            r2_checkbox.pack(pady=10, padx=20, anchor="w")

            #Toggle Legend
            legend_var = tk.BooleanVar(value=self.plotter.show_legend)  # Default value for legend visibility
            legend_checkbox = tk.Checkbutton(adv_window, text="Toggle Legend", variable=legend_var, font=("Arial", 12), bg="#f0f0f0", fg="black")       
            legend_checkbox.pack(pady=10, padx=20, anchor="w")

            def save_scatter_settings():
                self.plotter.show_best_fit = best_fit_var.get()
                self.plotter.show_confidence_interval = not ci_var.get()
                self.plotter.show_equation = equation_var.get()
                self.plotter.show_r = r_var.get()
                self.plotter.show_r2 = r2_var.get()
                self.plotter.show_legend = legend_var.get()
                adv_window.destroy()

            save_button = tk.Button(adv_window, text="Save", font=("Arial", 12), command=save_scatter_settings)
            save_button.pack(pady=(20, 10))

        # options for box plot
        elif self.plot_type_combo.get() == "Box Plot":
            box_label = tk.Label(adv_window, text="Box Plot", font=("Arial", 12), bg="#f0f0f0",fg="black")
            box_label.pack(pady=0)

            outliers_var = tk.BooleanVar(value=self.plotter.show_outliers)
            outliers_checkbox = tk.Checkbutton(adv_window, text="Show Outliers", variable=outliers_var,
                                               font=("Arial", 12), bg="#f0f0f0", fg="black")
            outliers_checkbox.pack(pady=10)

            def save_box_settings():
                self.plotter.show_outliers = outliers_var.get()
                adv_window.destroy()

            save_button = tk.Button(adv_window, text="Save", font=("Arial", 12), command=save_box_settings)
            save_button.pack(pady=(20, 10))

        elif self.plot_type_combo.get() == "Pie Chart":
            Pie_label = tk.Label(adv_window, text="Pie Chart", font=("Arial", 12), bg="#f0f0f0", fg="black")
            Pie_label.pack(pady=0)

            # Display Option Dropdown
            display_label = tk.Label(adv_window, text="Display beside pie sections:", font=("Arial", 12), bg="#f0f0f0", fg="black")
            display_label.pack(pady=(10, 0))

            display_var = tk.StringVar(
                value=self.plotter.pie_display_option if hasattr(self.plotter, "pie_display_option") else "count")
            display_dropdown = ttk.Combobox(adv_window, textvariable=display_var, font=("Arial", 12), state="readonly")
            display_dropdown['values'] = ["count", "percentage", "both", "neither"]
            display_dropdown.pack(pady=5)

            # Labels Toggle
            labels_var = tk.BooleanVar(
                value=self.plotter.pie_show_labels if hasattr(self.plotter, "pie_show_labels") else True)
            labels_checkbox = tk.Checkbutton(adv_window, text="Show Labels", variable=labels_var, font=("Arial", 12),
                                             bg="#f0f0f0", fg="black")
            labels_checkbox.pack(pady=5)

            # Legend Toggle
            legend_var = tk.BooleanVar(
                value=self.plotter.pie_show_legend if hasattr(self.plotter, "pie_show_legend") else True)
            legend_checkbox = tk.Checkbutton(adv_window, text="Show Legend", variable=legend_var, font=("Arial", 12),
                                             bg="#f0f0f0", fg="black")
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
                }, window = adv_window, confirmation_text="Pie chart settings saved.")
            )
            save_button.pack(pady=(20, 10))

        elif self.plot_type_combo.get() == "Histogram":
            hist_label = tk.Label(adv_window, text="Histogram", font=("Arial", 12), bg="#f0f0f0",fg="black")
            hist_label.pack(pady=0)

            # Number of bins
            bins_label = tk.Label(adv_window, text="Number of bins:", font=("Arial", 12), bg="#f0f0f0", fg="black") 
            bins_label.pack(pady=(10, 0))

            bins_entry = tk.Entry(adv_window, font=("Arial", 12), width=10, bg="white", fg="black", bd=1, highlightthickness=0)
            bins_entry.pack(pady=5)
            bins_entry.insert(0, str(self.plotter.bin_size))

            # kernel density estimation
            kde_var = tk.BooleanVar(value=self.plotter.kde_bool)
            kde_checkbox = tk.Checkbutton(adv_window, text="Show Kernel Density Estimation", variable=kde_var,
                                          font=("Arial", 12), bg="#f0f0f0", fg="black")
            kde_checkbox.pack(pady=5)

            # Save Button
            save_button = tk.Button(
                adv_window,
                text="Save",
                font=("Arial", 12),
                command=lambda: self.save_advanced_settings({
                    'bin_size': (bins_entry, int),
                    'kde_bool': (kde_var, bool),
                }, window= adv_window, confirmation_text="Histogram settings saved.")
            )
            save_button.pack(pady=(20, 10))

        elif self.plot_type_combo.get() == "Pairplot":

            # Instruction label
            instruction_label = tk.Label(
                adv_window,
                text="Enter variable names separated by commas:", font=("Arial", 12), bg="#f0f0f0", fg="black")
            instruction_label.pack(pady=(10, 5))

            # Text box for user input
            pairplot_entry = tk.Entry(adv_window, font=("Arial", 12), width=30, bg="white", fg="black", bd=1, highlightthickness=0)

            # Pre-fill the text box with the previously saved value (if any)
            if hasattr(self.plotter, 'pairplot_variables') and self.plotter.pairplot_variables:
                pairplot_entry.insert(0, self.plotter.pairplot_variables)

            pairplot_entry.pack(pady=(10, 20), padx=30)

            # Save button
            def save_pairplot_settings():
                # Save the user input to the plotter object
                self.plotter.pairplot_variables = pairplot_entry.get()
                adv_window.destroy()  # Close the advanced settings window

            save_button = tk.Button(
                adv_window,
                text="Save",
                font=("Arial", 12),
                command=save_pairplot_settings
            )
            save_button.pack(pady=(20, 10))

        elif self.plot_type_combo.get() == "Violin Plot":
            Violin_label = tk.Label(adv_window, text="Violin Plot", font=("Arial", 12), bg="#f0f0f0", fg="black")
            Violin_label.pack(pady=0)

            if self.column3_combo.get() == "":
                if col1 in self.categorical_columns and col2 in self.numeric_columns:
                    Violin_label_label = tk.Label(adv_window, text="Violin Graph", font=("Arial", 12), bg="#f0f0f0", fg="black")
                    Violin_label_label.pack(pady=0)

                    # Entry box for input category names
                    input_cat_label = tk.Label(adv_window, text="Input Group (separated by \",\"): ", bg="#f0f0f0", fg="black",)
                    input_cat_label.pack(pady=10)
                    input_cat_entry = tk.Entry(adv_window, font=("Arial", 12), width=20, bg="white", fg="black", bd=1, highlightthickness=0)
                    input_cat_entry.pack(pady=10)
                    input_cat_entry.insert(0, self.plotter.input_cat)

                    # Checkbox for Anova
                    anova_var = tk.BooleanVar(value=self.plotter.anova_bool)
                    anova_checkbox = tk.Checkbutton(adv_window, text="Perform ANOVA/T-Test", variable=anova_var,
                                                    font=("Arial", 12), bg="#f0f0f0", fg="black")
                    anova_checkbox.pack(pady=10)

                    save_button = tk.Button(
                        adv_window,
                        text="Save",
                        font=("Arial", 12),
                        command=lambda: self.save_advanced_settings({
                            'input_cat': (input_cat_entry, str),
                            'anova_bool': (anova_var, bool)
                        }, window=adv_window, confirmation_text="Violin plot settings saved.")
                    )

                    save_button.pack(pady=(20, 10))

                elif col1 in self.numeric_columns and col2 in self.numeric_columns:
                    # check box for 1 sample t-test
                    t1_marker_var = tk.BooleanVar(value=self.plotter.t1_bool)
                    t1_marker_checkbox = tk.Checkbutton(adv_window, text="Plot 1 sample t-test", variable=t1_marker_var,
                                                        font=("Arial", 12), bg="#f0f0f0", fg="black")
                    t1_marker_checkbox.pack(pady=10)

                    # reference values for 1 sample t-test
                    t1_col1_ref_lab = tk.Label(adv_window, text="Variable 1 reference value:", font=("Arial", 12),
                                               bg="#f0f0f0", fg="black")
                    t1_col1_ref_lab.pack(pady=0)
                    t1_col1_ref_entry = tk.Entry(adv_window, font=("Arial", 12), width=10, bg="white", fg="black", bd=1, highlightthickness=0)
                    t1_col1_ref_entry.pack(pady=10)
                    t1_col1_ref_entry.insert(0, str(self.plotter.t1_ref1))

                    t1_col2_ref_lab = tk.Label(adv_window, text="Variable 2 reference value:", font=("Arial", 12), bg="#f0f0f0", fg="black")
                    t1_col2_ref_lab.pack(pady=0)
                    t1_col2_ref_entry = tk.Entry(adv_window, font=("Arial", 12), width=10, bg="white", fg="black", bd=1, highlightthickness=0)
                    t1_col2_ref_entry.pack(pady=10)
                    t1_col2_ref_entry.insert(0, str(self.plotter.t1_ref2))

                    # check box for 2 sample t-test
                    t2_marker_var = tk.BooleanVar(value=self.plotter.t2_bool)
                    t2_marker_checkbox = tk.Checkbutton(adv_window, text="Plot 2 sample t-test", variable=t2_marker_var,
                                                        font=("Arial", 12), bg="#f0f0f0",fg="black")
                    t2_marker_checkbox.pack(pady=10)

                    save_button = tk.Button(
                        adv_window,
                        text="Save",
                        font=("Arial", 12),
                        command=lambda: self.save_advanced_settings({
                            't1_bool': (t1_marker_var, bool),
                            't2_bool': (t2_marker_var, bool),
                            't1_ref1': (t1_col1_ref_entry, float),
                            't1_ref2': (t1_col2_ref_entry, float),
                        }, window= adv_window, confirmation_text="Violin plot settings saved.")
                    )
                    save_button.pack(pady=(20, 10))

            else:
                # anova boolean marker
                anova_var = tk.BooleanVar(value=self.plotter.anova_bool)
                anova_checkbox = tk.Checkbutton(adv_window, text="Perform ANOVA", variable=anova_var,
                                                font=("Arial", 12), bg="#f0f0f0", fg="black")
                anova_checkbox.pack(pady=10)

                # Save Button
                save_button = tk.Button(
                    adv_window,
                    text="Save",
                    font=("Arial", 12),
                    command=lambda: self.save_advanced_settings({
                        'anova_bool': (anova_var, bool),
                    }, window= adv_window, confirmation_text="Violin plot settings saved.")
                )
                save_button.pack(pady=(20, 10))

    def save_advanced_settings(self, widget_map, confirmation_text="Advanced settings saved successfully!", window=None):
        for attr, (widget, cast) in widget_map.items():
            try:
                setattr(self.plotter, attr, cast(widget.get()))
            except Exception:
                setattr(self.plotter, attr, "")
        if window:
            window.destroy()

    def update_plot_selection(self, event):
        col1 = self.column1_combo.get()
        col2 = self.column2_combo.get()
        col3 = self.column3_combo.get()

            # Reset the plot types if everything is blank
        if col1 == "" and col2 == "" and col3 == "":
            self.plot_type_combo["values"] = ["Heat Map", "Pairplot"]
            self.plot_type_combo.set("")
            self.plot_type_combo.config(state="readonly")
            self.plot_button.config(state="disabled")
            self.analyze_button.config(state="disabled")
            self.advanced_button.config(state="disabled")
            return

        if col1:
            self.plot_type_combo.config(state="readonly")

            # Update plot type options based on new Column 1
            self.plot_type_combo.set("")

            if col1 in self.numeric_columns and col2 == "" and col3 == "":
                self.plot_type_combo["values"] = ["Histogram", "Pie Chart"]
            elif col1 == "" and col2 == "" and col3 == "":
                self.plot_type_combo["values"] = ["Pair Plot", "Heat Map"]
            elif col1 in self.numeric_columns and col2 in self.categorical_columns:
                self.plot_type_combo["values"] = [""]
            elif col1 in self.categorical_columns and col2 in self.numeric_columns:
                self.plot_type_combo["values"] = ["Bar", "Violin Plot", "Box Plot"]
            elif col1 in self.numeric_columns and col2 in self.numeric_columns and col3 == "":
                self.plot_type_combo["values"] = ["Scatter", "Line", "Bar", "Violin Plot", "Box Plot"]
            elif col1 in self.numeric_columns and col2 in self.numeric_columns and col3 in self.numeric_columns:
                self.plot_type_combo["values"] = ["Scatter", "Bar", "Violin Plot", "Box Plot"]
            elif col1 in self.categorical_columns and col2 in self.categorical_columns:
                self.plot_type_combo["values"] = ["Heat Map"]

        # Enable the third dropdown only if both col1 and col2 are numerical
        if col1 in self.numeric_columns and col2 in self.numeric_columns:
            self.column3_combo.config(state="readonly")
            self.column3_combo['values'] = [""] + self.numeric_columns
        else:
            self.column3_combo.set("")
            self.column3_combo.config(state="disabled")

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

    def show_scrollable_results(self, text):
        # Create a new Toplevel window
        result_window = tk.Toplevel(self.root)
        result_window.title("Analysis Results")
        result_window.geometry("600x400")

        # Create a Text widget with a scrollbar
        text_frame = tk.Frame(result_window)
        text_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        text_widget = tk.Text(text_frame, wrap="word", yscrollcommand=scrollbar.set, font=("Arial", 12))
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text_widget.yview)

        # Insert the text into the Text widget
        text_widget.insert("1.0", text)
        text_widget.config(state="disabled")  # Make the Text widget read-only

    #heatmap
    def select_color(self, which):
        color = colorchooser.askcolor(title=f"Select {which} color")[1]
        if color:
            if which == 'low':
                self.plotter.heatmap_low_color = color
                self.low_color_display.config(bg=color)
            else:
                self.plotter.heatmap_high_color = color
                self.high_color_display.config(bg=color)

    def plot_type_selected(self, event):
        plot_type = self.plot_type_combo.get()

        # Show/hide color selection based on plot type
        if plot_type == "Heat Map":
            self.color_selection_frame.pack(pady=10)
        else:
            self.color_selection_frame.pack_forget()

        # Rest of existing method...
        col1 = self.column1_combo.get()
        col2 = self.column2_combo.get()
        col3 = self.column3_combo.get()

        if plot_type != "":
            self.plot_button.config(state="normal")
            self.advanced_button.config(state="normal")
            self.analyze_button.config(state="normal")
        else:
            self.plot_button.config(state="disabled")
            self.analyze_button.config(state="disabled")


    def graph_info(self):
        # Get the selected plot type
        plot_type = self.plot_type_combo.get()

        # Define information for each plot type
        if plot_type == "Bar":
            info_text = (
                "Bar Graph Info:\n\n"
                "- A bar graph is used to compare categories of data.\n\n"
                "- X-axis: Categorical variable.\n"
                "- Y-axis: Numerical variable.\n\n"
                "- Example: Sales by product category."
            )
        elif plot_type == "Scatter":
            info_text = (
                "Scatter Plot Info:\n\n"
                "- A scatter plot is used to show relationships between two numerical variables.\n\n"
                "- X-axis: Numerical variable.\n"
                "- Y-axis: Numerical variable.\n\n"
                "- Example: Age vs. Income."
            )
        elif plot_type == "Line":
            info_text = (
                "Line Graph Info:\n\n"
                "- A line graph is used to show trends over time or continuous data.\n\n"
                "- X-axis: Numerical variable (e.g., time).\n"
                "- Y-axis: Numerical variable.\n\n"
                "- Example: Stock prices over time."
            )
        elif plot_type == "Pie Chart":
            info_text = (
                "Pie Chart Info:\n\n"
                "- A pie chart is used to show proportions of categories.\n\n"
                "- Only one categorical variable is required.\n\n"
                "- Example: Market share by company."
            )
        elif plot_type == "Heat Map":
            info_text = (
                "Heat Map Info:\n\n"
                "- A heat map is used to visualize data in a matrix format with color coding.\n\n"
                "- X-axis: Categorical variable.\n"
                "- Y-axis: Categorical variable.\n\n"
                "- Example: Correlation matrix."
            )
        elif plot_type == "Violin Plot":
            info_text = (
                "Violin Plot Info:\n\n"
                "- A violin plot is used to show the distribution of numerical data across categories.\n\n"
                "- X-axis: Categorical variable.\n"
                "- Y-axis: Numerical variable.\n\n"
                "- Example: Test scores by class."
            )
        elif plot_type == "Box Plot":
            info_text = (
                "Box Plot Info:\n\n"
                "- A box plot is used to show the distribution of numerical data.\n\n"
                "- X-axis: Categorical variable.\n"
                "- Y-axis: Numerical variable.\n\n"
                "- Example: Salary distribution by department."
            )
        elif plot_type == "Histogram":
            info_text = (
                "Histogram Info:\n\n"
                "- A histogram is used to show the distribution of a single numerical variable.\n\n"
                "- X-axis: Numerical variable (bins).\n"
                "- Y-axis: Frequency.\n\n"
                "- Example: Age distribution in a population."
            )
        elif plot_type == "Pairplot":
            info_text = (
                "Pairplot Info:\n\n"
                "- A pairplot is used to visualize pairwise relationships in a dataset.\n"
                "- Displays scatter plots for numerical variables and histograms for distributions.\n"
            )
        else:
            info_text = "Please select a valid plot type."

        # Display the information in a message box
        messagebox.showinfo("Graph Info", info_text)