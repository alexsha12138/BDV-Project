import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import pandas as pd
from tkinter import messagebox

class PlotManager:
    def __init__(self):
        # Default advanced settings
        # bar plots
        self.t1_bool = False
        self.t1_ref1 = 0
        self.t1_ref2 = 0
        self.t2_bool = False

        self.show_best_fit = True

        self.input_cat = " "
        self.anova = False

        # pie chart
        self.pie_display_option = "count"   # "count", "percentage", "both", "neither"
        self.pie_show_labels = True
        self.pie_show_legend = True



        
    def plot(self, df, plot_type, col1=None, col2=None, xres=1280, yres=720, title=None, xlabel=None, ylabel=None):
        # Convert pixel resolution to inches (DPI is typically 100)
        dpi = 100
        width = xres / dpi
        height = yres / dpi
        fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)

        try:
            if plot_type == "Bar":
                if pd.api.types.is_numeric_dtype(df[col1]) and pd.api.types.is_numeric_dtype(df[col2]):
                    # Call the specialized two-numeric-column bar plot
                    self.plot_bar_2_num(df, col1, col2,
                        t1_bool=self.t1_bool,
                        t1_ref1=self.t1_ref1,
                        t1_ref2=self.t1_ref2,
                        t2_bool=self.t2_bool)
                elif pd.api.types.is_string_dtype(df[col1]) and pd.api.types.is_numeric_dtype(df[col2]):
                    self.plot_bar_cat_num(df, col1, col2, 
                                          input_cat = self.input_cat)

            elif plot_type == "Scatter":
                self.plot_scatter(df, col1, col2)
            elif plot_type == "Line":
                self.plot_line(df, col1, col2)
            elif plot_type == "Pie Chart":
                self.plot_pie(df, col1, ax)
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

            plt.xticks(rotation=0)
            plt.tight_layout()
            plt.show()

        except Exception as e:
            messagebox.showerror("Plot Error", f"Failed to generate plot:\n{e}")
    
    def plot_bar_cat_num (self, df, col1, col2, input_cat):
        # Normalize user input
        input_list_raw = [item.strip() for item in input_cat.split(",")]
        input_list_lower = [item.lower() for item in input_list_raw]

        # Clean and lowercase column values for filtering
        df[col1] = df[col1].astype(str).str.strip()
        df['__lower_temp__'] = df[col1].str.lower()

        # Filter using lowercase match
        filtered_df = df[df['__lower_temp__'].isin(input_list_lower)].copy()

        # Replace country names in filtered_df with original casing from input
        casing_map = {name.lower(): name for name in input_list_raw}
        filtered_df[col1] = filtered_df['__lower_temp__'].map(casing_map)

        avg_df = filtered_df.groupby(col1)[col2].mean().reset_index()
        avg_df.columns = [col1, f"Average {col2}"]

        sns.barplot(data=avg_df, x=col1, y=f'Average {col2}', hue = col1, palette='pastel', legend = False)
        plt.title(f'Average {col2} by {col1}')
        plt.ylabel(f'Average {col2}')
        plt.xlabel(col1.capitalize())
        plt.tight_layout()

    def plot_bar_2_num(self, df, col1, col2, t1_bool, t1_ref1, t1_ref2, t2_bool):
        titles = [col1, col2]
        var1 = df[col1]
        var2 = df[col2]
        
        var1_t, var1_p = stats.ttest_1samp(var1, t1_ref1)
        var2_t, var2_p = stats.ttest_1samp(var2, t1_ref2)
        t2_t, t2_p = stats.ttest_ind(var1, var2)

        sns.barplot(x = titles, y = [var1.mean(), var2.mean()], hue = titles, palette = ["lightcoral","skyblue"])
        two_bar_y = int(max(var1.mean(), var2.mean()))

        if t1_bool == True:
            
            plt.text(0, two_bar_y*1.02966, self.p_val_mark(var1_p), ha = "center", va = "bottom", fontsize = 18)
            plt.text(1, two_bar_y*1.02966, self.p_val_mark(var2_p), ha = "center", va = "bottom", fontsize = 18)

            plt.text (0, var1.mean(), f"P: {self.round_num(var1_p)}", ha = "center", va = "bottom", fontsize=14)
            plt.text (1, var2.mean(), f"P: {self.round_num(var2_p)}", ha = "center", va = "bottom", fontsize=14)

        if t2_bool == True:
            two_bar_y = max(var1.mean(), var2.mean()) * 1.09322033898
            plt.plot([0,0,1,1], [two_bar_y,two_bar_y*1.00847457627, two_bar_y*1.00847457627, two_bar_y], lw=1.5, color= 'black')
            plt.text(0.5, two_bar_y*1.00423728814, self.p_val_mark(t2_p), ha = "center", va = "bottom", fontsize=18)
            plt.text(0.5, two_bar_y*0.95762711864, f"P: {self.round_num(t2_p)}", ha = "center", va = "bottom", fontsize=14)

        plt.ylim(0,two_bar_y*1.10169491525)
        print(two_bar_y)



    def plot_scatter(self, df, col1, col2):
            sns.scatterplot(x=col1, y=col2, data=df)

            if self.show_best_fit:
                sns.regplot(x=col1, y=col2, data=df, scatter=False, line_kws={"color": "red"})

            plt.xlabel(col1)
            plt.ylabel(col2)


    def plot_line(self, df, col1, col2):
        plt.plot(df[col1], df[col2], marker='o')


    def plot_pie(self, df, col1, ax):
        counts = df[col1].value_counts()
        labels = counts.index
        sizes = counts.values

        def autopct_func(pct, allvals=sizes):
            count = int(round(pct / 100. * sum(allvals)))
            if self.pie_display_option == "percentage":
                return f"{pct:.1f}%"
            elif self.pie_display_option == "count":
                return f"{count}"
            elif self.pie_display_option == "both":
                return f"{pct:.1f}%\n({count})"
            elif self.pie_display_option == "neither":
                return None
            else:
                return None

        
        if self.pie_display_option != "neither":
            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels if self.pie_show_labels else None,
                autopct=autopct_func,
                startangle=90
            )
        else:
            wedges, texts = ax.pie(
                sizes,
                labels=labels if self.pie_show_labels else None,
                startangle=90
            )

        if self.pie_show_legend:
            ax.legend(wedges, labels, title=col1, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    def plot_heatmap(self, df):
        sns.heatmap(df.corr(), annot=True, cmap='coolwarm', fmt=".2f")

    def plot_violin(self, df, col1, col2):
        # Melt the data for seaborn
        df_melted = df[[col1, col2]].melt(var_name="Group", value_name="Value")
        sns.violinplot(data=df_melted, x="Group", y="Value", inner="box", palette="Set2") 

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

    def p_val_mark(self, p):
        if p < 0.001:
            return ("***")
        elif p < 0.01:
            return ("**")
        elif p < 0.05:
            return ("*")
        else:
            return ("")
        
    def round_num (self, num):
        if num < 0.001 or num > 1000:
            return f"{num:.2e}"
        else:
            return f"{num:.2f}"