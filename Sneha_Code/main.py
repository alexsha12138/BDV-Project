import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class CSVPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Plotter")

        self.df = None
        self.columns = []

        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        # Load CSV button
        self.load_button = tk.Button(self.root, text="Load CSV", command=self.load_csv)
        self.load_button.pack(pady=10)

        # Plot type selection
        self.plot_type_label = tk.Label(self.root, text="Select plot type:")
        self.plot_type_label.pack(pady=5)
        self.plot_type_combo = ttk.Combobox(self.root, state="readonly",
                                            values=["Bar", "Scatter", "Line", "Pie Chart", "Heat Map", "Violin Plot",
                                                    "Box Plot", "Histogram"])
        self.plot_type_combo.pack(pady=5)
        self.plot_type_combo.bind("<<ComboboxSelected>>", self.update_column_selection)

        # Column selection dropdowns
        self.column1_label = tk.Label(self.root, text="Select first column:")
        self.column1_label.pack(pady=5)
        self.column1_combo = ttk.Combobox(self.root, state="disabled")
        self.column1_combo.pack(pady=5)

        self.column2_label = tk.Label(self.root, text="Select second column (if required):")
        self.column2_label.pack(pady=5)
        self.column2_combo = ttk.Combobox(self.root, state="disabled")
        self.column2_combo.pack(pady=5)

        # Plot button
        self.plot_button = tk.Button(self.root, text="Plot Graph & Analyze", command=self.plot_graph, state="disabled")
        self.plot_button.pack(pady=20)

    def load_csv(self):
        """Open file dialog to select a CSV file and load the data."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        try:
            self.df = pd.read_csv(file_path)
            self.columns = list(self.df.columns)
            # Enable plot type selection
            self.plot_type_combo.config(state="readonly")
            messagebox.showinfo("CSV Loaded", "CSV file successfully loaded!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file: {e}")

    def update_column_selection(self, event):
        """Update the column selection options based on chosen plot type."""
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

    def perform_statistical_test(self, col1, col2):
        """Perform a two-tailed t-test and calculate confidence interval."""
        data1 = self.df[col1].dropna()
        data2 = self.df[col2].dropna()

        t_stat, p_value = stats.ttest_ind(data1, data2, equal_var=False)
        confidence_interval = stats.t.interval(0.95, len(data1) - 1, loc=data1.mean(), scale=stats.sem(data1))

        result_text = f"T-Test results:\nT-Statistic: {t_stat:.4f}\nP-Value: {p_value:.4f}\n" \
                      f"95% Confidence Interval for {col1}: {confidence_interval}"
        messagebox.showinfo("Statistical Analysis", result_text)
        print(result_text)

    def plot_graph(self):
        """Generate the selected plot type based on user choices and perform statistical analysis."""
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

        plt.figure(figsize=(10, 5))

        if plot_type == "Bar":
            plt.bar(self.df[col1].astype(str), self.df[col2], color='skyblue')
            plt.xlabel(col1)
            plt.ylabel(col2)
        elif plot_type == "Scatter":
            plt.scatter(self.df[col1], self.df[col2], color='blue')
            plt.xlabel(col1)
            plt.ylabel(col2)
        elif plot_type == "Line":
            plt.plot(self.df[col1], self.df[col2], marker='o')
            plt.xlabel(col1)
            plt.ylabel(col2)
        elif plot_type == "Pie Chart":
            plt.pie(self.df[col1].value_counts(), labels=self.df[col1].value_counts().index, autopct='%1.1f%%')
        elif plot_type == "Heat Map":
            sns.heatmap(self.df.corr(), annot=True, cmap='coolwarm', fmt=".2f")
        elif plot_type == "Violin Plot":
            sns.violinplot(x=self.df[col1], y=self.df[col2])
        elif plot_type == "Box Plot":
            sns.boxplot(x=self.df[col1], y=self.df[col2])
        elif plot_type == "Histogram":
            plt.hist(self.df[col1], bins=20, color='skyblue', edgecolor='black')
            plt.xlabel(col1)

        plt.title(f'{plot_type} of {col1} vs {col2}' if col2 else f'{plot_type} of {col1}')
        plt.xticks(rotation=45)
        plt.show()

        if col2:
            self.perform_statistical_test(col1, col2)


def main():
    root = tk.Tk()
    app = CSVPlotterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
