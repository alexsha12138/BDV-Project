import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import filedialog, ttk, colorchooser, messagebox
from matplotlib.colors import LinearSegmentedColormap


class CSVPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Plotter")
        self.df = None
        self.numerical_columns = []
        self.categorical_columns = []

        # Default colors for heatmap
        self.low_color = "#FFFFFF"  # Default to white
        self.high_color = "#FFFFFF"  # Default to blue

        self.create_widgets()

    def create_widgets(self):
        self.load_button = tk.Button(self.root, text="Load CSV", command=self.load_csv)
        self.load_button.pack(pady=10)

        self.upload_status_label = tk.Label(self.root, text="", fg="green")
        self.upload_status_label.pack(pady=5)

        self.column_frame = tk.Frame(self.root)
        self.column_frame.pack(pady=10)

        self.num_label = tk.Label(self.column_frame, text="Numerical Columns")
        self.num_label.grid(row=0, column=0)
        self.num_listbox = tk.Listbox(self.column_frame, height=10, width=30)
        self.num_listbox.grid(row=1, column=0, padx=10)

        self.cat_label = tk.Label(self.column_frame, text="Categorical Columns")
        self.cat_label.grid(row=0, column=1)
        self.cat_listbox = tk.Listbox(self.column_frame, height=10, width=30)
        self.cat_listbox.grid(row=1, column=1, padx=10)

        self.plot_type_label = tk.Label(self.root, text="Select plot type:")
        self.plot_type_label.pack(pady=5)
        self.plot_type_combo = ttk.Combobox(self.root, state="readonly",
                                            values=["Bar", "Scatter", "Line", "Pie Chart", "Heat Map", "Violin Plot",
                                                    "Box Plot", "Histogram"])
        self.plot_type_combo.pack(pady=5)
        self.plot_type_combo.bind("<<ComboboxSelected>>", self.update_column_selection)

        self.details_frame = tk.Frame(self.root)
        self.column1_label = tk.Label(self.details_frame, text="Select first column:")
        self.column1_combo = ttk.Combobox(self.details_frame, state="disabled")
        self.column2_label = tk.Label(self.details_frame, text="Select second column:")
        self.column2_combo = ttk.Combobox(self.details_frame, state="disabled")

        self.x_label_entry_label = tk.Label(self.details_frame, text="Enter the label for x-axis:")
        self.x_label_entry = tk.Entry(self.details_frame)
        self.y_label_entry_label = tk.Label(self.details_frame, text="Enter the label for y-axis:")
        self.y_label_entry = tk.Entry(self.details_frame)
        self.chart_title_entry_label = tk.Label(self.details_frame, text="Enter the chart title:")
        self.chart_title_entry = tk.Entry(self.details_frame)

        self.plot_button = tk.Button(self.details_frame, text="Plot Graph & Analyze", command=self.plot_graph,
                                     state="disabled")

        # Color selection buttons for heatmap (initially hidden)
        self.color_button_frame = tk.Frame(self.root)
        self.low_color_button = tk.Button(self.color_button_frame, text="Select the color for the lowest value",
                                          command=self.select_low_color)
        self.high_color_button = tk.Button(self.color_button_frame, text="Select the color for the highest value",
                                           command=self.select_high_color)

        # Color display labels for heatmap (initially hidden)
        self.low_color_display = tk.Label(self.color_button_frame, text="Lowest value", width=20, height=2,
                                          bg=self.low_color)
        self.high_color_display = tk.Label(self.color_button_frame, text="Highest value", width=20, height=2,
                                           bg=self.high_color)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            self.df = pd.read_csv(file_path)
            self.categorize_columns()
            self.upload_status_label.config(text="Upload Successful!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file: {e}")

    def categorize_columns(self):
        self.numerical_columns.clear()
        self.categorical_columns.clear()

        for col in self.df.columns:
            if pd.api.types.is_numeric_dtype(self.df[col]):
                self.numerical_columns.append(col)
            else:
                self.categorical_columns.append(col)

        self.num_listbox.delete(0, tk.END)
        self.cat_listbox.delete(0, tk.END)

        for col in self.numerical_columns:
            self.num_listbox.insert(tk.END, col)
        for col in self.categorical_columns:
            self.cat_listbox.insert(tk.END, col)

    def update_column_selection(self, event):
        plot_type = self.plot_type_combo.get()

        if plot_type in ["Scatter", "Line", "Violin Plot", "Box Plot"]:
            self.column1_combo['values'] = self.numerical_columns
            self.column2_combo['values'] = self.numerical_columns
        elif plot_type == "Bar":
            self.column1_combo['values'] = self.categorical_columns
            self.column2_combo['values'] = self.numerical_columns
        elif plot_type == "Pie Chart":
            self.column1_combo['values'] = self.categorical_columns
            self.column2_combo['values'] = []
        elif plot_type == "Heat Map":
            self.column1_combo['values'] = []
            self.column2_combo['values'] = []
            # Show and enable color selection only for Heat Map
            self.color_button_frame.pack(pady=5)
            self.low_color_button.pack(side=tk.LEFT, padx=10)
            self.high_color_button.pack(side=tk.LEFT, padx=10)
            self.low_color_display.pack(side=tk.LEFT, padx=5)
            self.high_color_display.pack(side=tk.LEFT, padx=5)
        elif plot_type == "Histogram":
            self.column1_combo['values'] = self.numerical_columns
            self.column2_combo['values'] = []

        self.column1_combo.config(state="normal" if self.column1_combo['values'] else "disabled")
        self.column2_combo.config(state="normal" if self.column2_combo['values'] else "disabled")

        self.details_frame.pack(pady=10)
        self.column1_label.pack()
        self.column1_combo.pack()
        self.column2_label.pack()
        self.column2_combo.pack()
        self.x_label_entry_label.pack()
        self.x_label_entry.pack()
        self.y_label_entry_label.pack()
        self.y_label_entry.pack()
        self.chart_title_entry_label.pack()
        self.chart_title_entry.pack()
        self.plot_button.pack(pady=10)
        self.plot_button.config(state="normal")

    def select_low_color(self):
        color = colorchooser.askcolor(title="Choose Low Range Color")[1]
        if color:
            self.low_color = color
            self.low_color_display.config(bg=self.low_color)

    def select_high_color(self):
        color = colorchooser.askcolor(title="Choose High Range Color")[1]
        if color:
            self.high_color = color
            self.high_color_display.config(bg=self.high_color)

    def plot_graph(self):
        plot_type = self.plot_type_combo.get()
        col1 = self.column1_combo.get()
        col2 = self.column2_combo.get()
        x_label = self.x_label_entry.get()
        y_label = self.y_label_entry.get()
        chart_title = self.chart_title_entry.get()

        plt.figure(figsize=(10, 5))
        if plot_type == "Bar":
            plt.bar(self.df[col1].astype(str), self.df[col2], color='skyblue', label=f'{col1} vs {col2}')
        elif plot_type == "Scatter":
            plt.scatter(self.df[col1], self.df[col2], color='red', label=f'{col1} vs {col2}')
        elif plot_type == "Line":
            plt.plot(self.df[col1], self.df[col2], marker='o', label=f'{col1} vs {col2}')
        elif plot_type == "Pie Chart":
            plt.pie(self.df[col1].value_counts(), labels=self.df[col1].value_counts().index, autopct='%1.1f%%')
        elif plot_type == "Heat Map":
            self.plot_custom_heatmap()
            return
        elif plot_type == "Violin Plot":
            sns.violinplot(x=self.df[col1], y=self.df[col2])
        elif plot_type == "Box Plot":
            sns.boxplot(x=self.df[col1], y=self.df[col2])
        elif plot_type == "Histogram":
            plt.hist(self.df[col1], bins=20, color='skyblue', edgecolor='black', label=col1)

        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(chart_title)
        plt.legend()
        plt.xticks(rotation=45)
        plt.show()

    def plot_custom_heatmap(self):
        numeric_df = self.df.select_dtypes(include=['number'])
        if numeric_df.empty:
            messagebox.showerror("Error", "No numeric data available for heatmap.")
            return

        cmap = LinearSegmentedColormap.from_list("custom_gradient", [self.low_color, self.high_color])
        plt.figure(figsize=(10, 8))
        sns.heatmap(numeric_df.corr(), annot=True, cmap=cmap, fmt=".2f")
        plt.title("Heatmap with Custom Gradient")
        plt.show()


def main():
    root = tk.Tk()
    app = CSVPlotterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
