import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
from tkinter import messagebox

class PlotManager:
    def plot(self, df, plot_type, col1=None, col2=None, xres=1280, yres=720, title=None, xlabel=None, ylabel=None):
        # Convert pixel resolution to inches (DPI is typically 100)
        dpi = 100
        width = xres / dpi
        height = yres / dpi
        plt.figure(figsize=(width, height), dpi=dpi)

        try:
            if plot_type == "Bar":
                self.plot_bar(df, col1, col2)
            elif plot_type == "Scatter":
                self.plot_scatter(df, col1, col2)
            elif plot_type == "Line":
                self.plot_line(df, col1, col2)
            elif plot_type == "Pie Chart":
                self.plot_pie(df, col1)
            elif plot_type == "Heat Map":
                self.plot_heatmap(df)
            elif plot_type == "Violin Plot":
                self.plot_violin(df, col1, col2)
            elif plot_type == "Box Plot":
                self.plot_box(df, col1, col2)
            elif plot_type == "Histogram":
                self.plot_hist(df, col1)
            else:
                raise ValueError("Unknown plot type")

            # plot title & x/y labels
            plot_title = title if title else (f"{plot_type} of {col1} vs {col2}" if col2 else f"{plot_type} of {col1}")
            x_label = xlabel if xlabel else col1
            y_label = ylabel if ylabel else col2

            plt.title(plot_title)
            if x_label: plt.xlabel(x_label)
            if y_label: plt.ylabel(y_label)

            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()

        except Exception as e:
            messagebox.showerror("Plot Error", f"Failed to generate plot:\n{e}")

    def plot_bar(self, df, col1, col2):
        plt.bar(df[col1].astype(str), df[col2], color='skyblue')
        plt.xlabel(col1)
        plt.ylabel(col2)

    def plot_scatter(self, df, col1, col2):
        plt.scatter(df[col1], df[col2])
        plt.xlabel(col1)
        plt.ylabel(col2)

    def plot_line(self, df, col1, col2):
        plt.plot(df[col1], df[col2], marker='o')
        plt.xlabel(col1)
        plt.ylabel(col2)

    def plot_pie(self, df, col1):
        counts = df[col1].value_counts()
        plt.pie(counts, labels=counts.index, autopct='%1.1f%%')

    def plot_heatmap(self, df):
        sns.heatmap(df.corr(), annot=True, cmap='coolwarm', fmt=".2f")

    def plot_violin(self, df, col1, col2):
        sns.violinplot(x=df[col1], y=df[col2])

    def plot_box(self, df, col1, col2):
        sns.boxplot(x=df[col1], y=df[col2])

    def plot_hist(self, df, col1):
        plt.hist(df[col1], bins=20, color='skyblue', edgecolor='black')
        plt.xlabel(col1)

    def perform_stat_test(self, df, col1, col2):
        data1 = df[col1].dropna()
        data2 = df[col2].dropna()
        t_stat, p_val = stats.ttest_ind(data1, data2, equal_var=False)
        ci = stats.t.interval(0.95, len(data1) - 1, loc=data1.mean(), scale=stats.sem(data1))
        result = f"T-Test:\nT = {t_stat:.4f}\nP = {p_val:.4f}\n95% CI for {col1}: {ci}"
        messagebox.showinfo("Statistical Analysis", result)