import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import scipy.stats as stats
from scipy.stats import linregress
import pandas as pd
from tkinter import messagebox
from statsmodels.stats.multicomp import pairwise_tukeyhsd


class PlotManager:
    def __init__(self):
        # Default advanced settings

        # Heatmap settings
        self.heatmap_low_color = "#FFFFFF"  # white
        self.heatmap_high_color = "#0000FF"  # blue
        self.heatmap_cmap = None  # Will be generated from the colors

        # bar plots
        self.t1_bool = False
        self.t1_ref1 = 0
        self.t1_ref2 = 0
        self.t2_bool = True
        self.order = False

        self.input_cat = " "
        self.anova = False

        # scatter
        self.show_best_fit = True
        self.show_confidence_interval = True
        self.show_best_fit = False
        self.show_equation = False
        self.show_r = False
        self.show_r2 = False
        self.show_legend = False

        # box
        self.show_outliers = True

        # violin
        self.anova_bool = True

        # pie chart
        self.pie_display_option = "count"  # "count", "percentage", "both", "neither"
        self.pie_show_labels = True
        self.pie_show_legend = True

        # histogram
        self.kde_bool = True
        self.bin_size = 20

        #line graph
        self.line_color = "#1f77b4"  # Default matplotlib blue
        self.marker_color = "#ff7f0e"  # Default matplotlib orange

    def plot(self, df, plot_type, col1=None, col2=None, col3=None, xres=1280, yres=720, title=None, xlabel=None,
             ylabel=None, title_font=14, text_font=12):
        # Convert pixel resolution to inches (DPI is typically 100)
        dpi = 100
        width = xres / dpi
        height = yres / dpi
        if plot_type != "Heat Map":
            fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)


        try:
            if plot_type == "Bar":
                if pd.api.types.is_numeric_dtype(df[col1]) and pd.api.types.is_numeric_dtype(df[col2]) and col3 == None:
                    # Call the specialized two-numeric-column bar plot
                    self.plot_bar_2_num(df, col1, col2,
                                        t1_bool=self.t1_bool,
                                        t1_ref1=self.t1_ref1,
                                        t1_ref2=self.t1_ref2,
                                        t2_bool=self.t2_bool)
                elif pd.api.types.is_numeric_dtype(df[col1]) and pd.api.types.is_numeric_dtype(
                        df[col2]) and pd.api.types.is_numeric_dtype(df[col3]):
                    self.plot_bar_3_num(df, col1, col2, col3, anova_bool=self.anova_bool)
                elif pd.api.types.is_string_dtype(df[col1]) and pd.api.types.is_numeric_dtype(df[col2]):
                    self.plot_bar_cat_num(df, col1, col2,
                                          input_cat=self.input_cat,
                                          anova_bool=self.anova_bool)

            elif plot_type == "Scatter":
                self.plot_scatter(df, col1, col2)
            elif plot_type == "Line":
                self.plot_line(df, col1, col2)
            elif plot_type == "Pie Chart":
                self.plot_pie(df, col1, ax)
            elif plot_type == "Heat Map":
                self.plot_heatmap(df)
            elif plot_type == "Violin Plot":
                self.plot_violin(
                    df,
                    col1,
                    col2,
                    col3,  # Pass None if no third variable is selected
                    t1_bool=self.t1_bool,
                    t1_ref1=self.t1_ref1,
                    t1_ref2=self.t1_ref2,
                    t2_bool=self.t2_bool,
                    anova_bool=self.anova_bool,
                    input_cat=self.input_cat
                )
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

            plt.title(plot_title, fontsize=title_font)
            if x_label: plt.xlabel(x_label, fontsize=text_font)
            if y_label: plt.ylabel(y_label, fontsize=text_font)

            plt.xticks(rotation=0)
            plt.tight_layout()
            plt.show()

        except Exception as e:
            messagebox.showerror("Plot Error", f"Failed to generate plot:\n{e}")
            plt.close(fig)  # Automatically close the figure if an error occurs
            raise e  # Re-raise the exception to handle it elsewhere

    def plot_bar_cat_num(self, df, col1, col2, input_cat, anova_bool):
        if input_cat.strip() == "":  # Check if input_cat is empty or contains only whitespace
            # No filtering, use the entire DataFrame
            avg_df = df.groupby(col1)[col2].mean().reset_index()
            avg_df.columns = [col1, f"Average {col2}"]
        else:
            # Normalize user input
            input_list_raw = [item.strip() for item in input_cat.split(",")]
            input_list_lower = [item.lower() for item in input_list_raw]

            # Clean and lowercase column values for filtering
            df[col1] = df[col1].astype(str).str.strip()
            df['__lower_temp__'] = df[col1].str.lower()

            # Filter using lowercase match
            filtered_df = df[df['__lower_temp__'].isin(input_list_lower)].copy()

            # Replace category names in filtered_df with original casing from input
            casing_map = {name.lower(): name for name in input_list_raw}
            filtered_df[col1] = filtered_df['__lower_temp__'].map(casing_map)

            avg_df = filtered_df.groupby(col1)[col2].mean().reset_index()
            avg_df.columns = [col1, f"Average {col2}"]

            # Sort by mean
            avg_df = avg_df.sort_values(by=f"Average {col2}", ascending=False)

            # Reorder input_list_raw to match sorted order
            sorted_categories = avg_df[col1].tolist()

        # Drop rows with NaN or Inf values in the relevant columns
        avg_df = avg_df.replace([float('inf'), float('-inf')], float('nan')).dropna()

        # Sort the DataFrame by the average values in descending order
        avg_df = avg_df.sort_values(by=f"Average {col2}", ascending=False)

        # Plot the bar graph
        sns.barplot(data=avg_df, x=col1, y=f'Average {col2}', hue=col1, palette='pastel', dodge=False)

        # Add horizontal guidelines based on y-axis tick marks
        y_ticks = plt.gca().get_yticks()
        for y in y_ticks:
            plt.axhline(y=y, color='gray', linestyle='--', linewidth=0.5, alpha=0.7)

        # Annotate the plot with p-values if ANOVA is selected
        if anova_bool:
            if input_cat.strip() == "":
                # If no input is provided, use all categories
                unique_categories = df[col1].unique()
                if len(unique_categories) == 2:
                    # Perform t-test for two groups
                    group1 = df[df[col1] == unique_categories[0]][col2]
                    group2 = df[df[col1] == unique_categories[1]][col2]
                    t2_t, t2_p = stats.ttest_ind(group1, group2, equal_var=False)

                    # Annotate t-test results
                    self.annotate_t_test_results(
                        group1, group2,
                        t1_bool=False, t2_bool=True,
                        t1_ref1=0, t1_ref2=0,
                        t2_p=t2_p
                    )
                elif len(unique_categories) > 2:
                    # Restructure the DataFrame for ANOVA
                    anova_df = pd.DataFrame()
                    for category in unique_categories:
                        anova_df[category] = df[df[col1] == category][col2].reset_index(drop=True)
                    print(anova_df.head())
                    anova_df = anova_df.dropna(how="any")
                    # Perform ANOVA for multiple groups using the restructured DataFrame
                    sorted_categories = avg_df.sort_values(by=f"Average {col2}", ascending=False)[col1].tolist()
                    self.annotate_anova_results(anova_df, sorted_categories, use_mean=True)
            else:
                # If input is provided, use the filtered categories
                if len(input_list_raw) == 2:
                    # Perform t-test for two groups
                    group1 = filtered_df[filtered_df[col1] == input_list_raw[0]][col2]
                    group2 = filtered_df[filtered_df[col1] == input_list_raw[1]][col2]
                    t2_t, t2_p = stats.ttest_ind(group1, group2, equal_var=False)

                    # Annotate t-test results
                    self.annotate_t_test_results(
                        group1, group2,
                        t1_bool=False, t2_bool=True,
                        t1_ref1=0, t1_ref2=0,
                        t2_p=t2_p
                    )
                elif len(input_list_raw) > 2:
                    # Restructure the DataFrame for ANOVA
                    anova_df = pd.DataFrame()
                    anova_df = anova_df.dropna(how="any")
                    for category in input_list_raw:
                        anova_df[category] = filtered_df[filtered_df[col1] == category][col2].reset_index(drop=True)
                    print(anova_df.head())
                    # Perform ANOVA for multiple groups using the restructured DataFrame
                    self.annotate_anova_results(anova_df, sorted_categories, use_mean=True)

    def plot_bar_2_num(self, df, col1, col2, t1_bool, t1_ref1, t1_ref2, t2_bool):
        titles = [col1, col2]
        var1 = df[col1]
        var2 = df[col2]

        # Perform two-sample t-test
        t2_t, t2_p = stats.ttest_ind(var1, var2)

        # Plot the bar chart
        sns.barplot(x=titles, y=[var1.mean(), var2.mean()], hue=titles, palette=["lightcoral", "skyblue"])

        # Add horizontal guidelines based on y-axis tick marks
        y_ticks = plt.gca().get_yticks()
        for y in y_ticks:
            plt.axhline(y=y, color='gray', linestyle='--', linewidth=0.5, alpha=0.7)

        # Annotate t-test results
        self.annotate_t_test_results(var1, var2, t1_bool, t2_bool, t1_ref1, t1_ref2, t2_p)

    def plot_bar_3_num(self, df, col1, col2, col3, anova_bool):
        titles = [col1, col2, col3]
        means = {col: df[col].mean() for col in titles}
        sorted_means = sorted(means.items(), key=lambda x: x[1], reverse=True)

        sorted_titles = [item[0] for item in sorted_means]
        sorted_values = [item[1] for item in sorted_means]

        sns.barplot(x=sorted_titles, y=sorted_values, palette=["lightcoral", "skyblue", "lightgreen"])

        # Add horizontal guidelines based on y-axis tick marks
        y_ticks = plt.gca().get_yticks()
        for y in y_ticks:
            plt.axhline(y=y, color='gray', linestyle='--', linewidth=0.5, alpha=0.7)

        if anova_bool:

            self.annotate_anova_results(df, sorted_titles, use_mean=True)

    def plot_scatter(self, df, col1, col2, col3=None):
        # Plot col2 on the primary y-axis using Seaborn
        sns.scatterplot(data=df, x=col1, y=col2, color="tab:blue", label=col2)
        slope, intercept, r_value, p_value, std_err = linregress(df[col1], df[col2])

        # Create a secondary y-axis if col3 is provided
        if col3:
            ax1 = plt.gca()  # Get the current axes for the primary y-axis
            ax2 = ax1.twinx()  # Create a secondary y-axis
            sns.scatterplot(data=df, x=col1, y=col3, color="tab:orange", label=col3, ax=ax2)

            # Set labels for the secondary y-axis
            ax2.set_ylabel(col3, color="tab:orange")
            ax2.tick_params(axis="y", labelcolor="tab:orange")

             # Combine legends from both axes
            handles1, labels1 = ax1.get_legend_handles_labels()  # Get legend handles and labels from ax1
            handles2, labels2 = ax2.get_legend_handles_labels()  # Get legend handles and labels from ax2
            ax2.legend(handles=handles1 + handles2, labels=labels1 + labels2, loc="upper right")  # Combine legends
        else:
            # Add legend for a single y-variable
            if self.show_legend:
                plt.legend(loc="upper right")  # Show the legend
            else:
                plt.gca().legend().remove()  # Hide the legend

        # Set labels for the primary y-axis and x-axis
        plt.xlabel(col1)
        plt.ylabel(col2, color="tab:blue")
        plt.tick_params(axis="y", labelcolor="tab:blue")

        if self.show_best_fit:
            self.line_equation = f"y = {slope:.2f}x + {intercept:.2f}"  # Store the equation
            sns.regplot(x=col1, y=col2, data=df, ci=95 if self.show_confidence_interval else None, scatter=False,
                        line_kws={"color": "red"})
            
        x_pos = df[col1].min() + (df[col1].max() - df[col1].min()) * 0.02  # Slightly offset from the left
        y_pos = df[col2].max() - (df[col2].max() - df[col2].min()) * 0.02 

        if self.show_equation and hasattr(self, "line_equation"):
            plt.text(
                x=x_pos,  
                y=y_pos, 
                s=self.line_equation,
                color="red",
                fontsize=10,
                bbox=dict(facecolor="white", alpha=0.5, edgecolor="none")
            )

        if self.show_r:
            plt.text(x=x_pos, y=y_pos - (df[col2].max() - df[col2].min()) * 0.05,
                     s=f"R = {r_value:.2f}", color="red", fontsize=10,
                     bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"))

        if self.show_r2:
            r_squared = r_value ** 2
            plt.text(x=x_pos, y=y_pos - (df[col2].max() - df[col2].min()) * 0.1,
                     s=f"R² = {r_squared:.2f}", color="red", fontsize=10,
                     bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"))

    def plot_line(self, df, col1, col2):
        # Sort the DataFrame by the x-axis column (col1) in ascending order
        sorted_df = df.sort_values(by=col1)

        # If col2 is None (plotting all numerical columns against col1)
        if col2 is None:
            for column in df.columns:
                if column != col1 and pd.api.types.is_numeric_dtype(df[column]):
                    plt.plot(sorted_df[col1], sorted_df[column],
                             marker='o',
                             color=self.line_color,
                             markerfacecolor=self.marker_color,
                             label=column)
            plt.legend()
        else:
            plt.plot(sorted_df[col1], sorted_df[col2],
                     marker='o',
                     color=self.line_color,
                     markerfacecolor=self.marker_color)

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
        # Create colormap from selected colors
        self.heatmap_cmap = LinearSegmentedColormap.from_list(
            "custom_heatmap",
            [self.heatmap_low_color, self.heatmap_high_color]
        )

        numeric_df = df.select_dtypes(include=['number'])
        if numeric_df.empty:
            raise ValueError("No numeric data available for heatmap.")

        plt.figure(figsize=(10, 8))
        sns.heatmap(numeric_df.corr(), annot=True, cmap=self.heatmap_cmap, fmt=".2f")
        plt.title("Correlation Heatmap")

    def plot_violin(self, df, col1, col2, col3, t1_bool, t1_ref1, t1_ref2, t2_bool, anova_bool, input_cat):
        # Check if col1 categorical variable (indicating categorical vs numerical data)
        if pd.api.types.is_string_dtype(df[col1]):
            # if nothing is entered in the input box, use the entire DataFrame
            if input_cat.strip() == "":  # Check if input_cat is empty or contains only whitespace
                # No filtering, use the entire DataFrame
                avg_df = df.groupby(col1)[col2].mean().reset_index()
                avg_df.columns = [col1, f"Average {col2}"]

                # Sort categories by mean in descending order
                sorted_categories = avg_df.sort_values(by=f"Average {col2}", ascending=False)[col1]
                df[col1] = pd.Categorical(df[col1], categories=sorted_categories, ordered=True)

                # Plot the violin plot for all categories
                sns.violinplot(data=df, x=col1, y=col2, palette='pastel', inner='box')
            else:
                # Normalize user input
                input_list_raw = [item.strip() for item in input_cat.split(",")]
                input_list_lower = [item.lower() for item in input_list_raw]

                # Clean and lowercase column values for filtering
                df[col1] = df[col1].astype(str).str.strip()
                df['__lower_temp__'] = df[col1].str.lower()

                # Filter using lowercase match
                filtered_df = df[df['__lower_temp__'].isin(input_list_lower)].copy()

                # Replace category names in filtered_df with original casing from input
                casing_map = {name.lower(): name for name in input_list_raw}
                filtered_df[col1] = filtered_df['__lower_temp__'].map(casing_map)

                avg_df = filtered_df.groupby(col1)[col2].mean().reset_index()
                avg_df.columns = [col1, f"Average {col2}"]

                # Sort categories by mean in descending order
                sorted_categories = avg_df.sort_values(by=f"Average {col2}", ascending=False)[col1]
                filtered_df[col1] = pd.Categorical(filtered_df[col1], categories=sorted_categories, ordered=True)

                # Plot the violin plot for filtered categories
                sns.violinplot(data=filtered_df, x=col1, y=col2, palette='pastel', inner='box')

            if anova_bool:
                if input_cat.strip() == "":
                    # If no input is provided, use all categories
                    unique_categories = df[col1].unique()
                    if len(unique_categories) == 2:
                        # Perform t-test for two groups
                        group1 = df[df[col1] == unique_categories[0]][col2]
                        group2 = df[df[col1] == unique_categories[1]][col2]
                        t2_t, t2_p = stats.ttest_ind(group1, group2, equal_var=False)

                        # Annotate t-test results
                        self.annotate_t_test_results(
                            group1, group2,
                            t1_bool=False, t2_bool=True,
                            t1_ref1=0, t1_ref2=0,
                            t2_p=t2_p,
                            use_mean=False
                        )
                    elif len(unique_categories) > 2:
                        # Restructure the DataFrame for ANOVA
                        anova_df = pd.DataFrame()
                        for category in unique_categories:
                            anova_df[category] = df[df[col1] == category][col2].reset_index(drop=True)
                        

                        anova_df_max = anova_df.max().max()

                        anova_df = anova_df.dropna(how="any")
                        print(anova_df_max)
                        # Perform ANOVA for multiple groups using the restructured DataFrame
                        sorted_categories = avg_df.sort_values(by=f"Average {col2}", ascending=False)[col1].tolist()
                        self.annotate_anova_results(anova_df, sorted_categories, use_mean=False, anova_df_max=anova_df_max)
                else:
                    # If input is provided, use the filtered categories
                    if len(input_list_raw) == 2:
                        # Perform t-test for two groups
                        group1 = filtered_df[filtered_df[col1] == input_list_raw[0]][col2]
                        group2 = filtered_df[filtered_df[col1] == input_list_raw[1]][col2]
                        t2_t, t2_p = stats.ttest_ind(group1, group2, equal_var=False)

                        # Annotate t-test results
                        self.annotate_t_test_results(
                            group1, group2,
                            t1_bool=False, t2_bool=True,
                            t1_ref1=0, t1_ref2=0,
                            t2_p=t2_p,
                            use_mean=False
                        )
                    elif len(input_list_raw) > 2:
                        # Restructure the DataFrame for ANOVA
                        anova_df = pd.DataFrame()
                        anova_df = anova_df.dropna(how="any")
                        for category in input_list_raw:
                            anova_df[category] = filtered_df[filtered_df[col1] == category][col2].reset_index(drop=True)
                        print(anova_df.head())
                        # Perform ANOVA for multiple groups using the restructured DataFrame
                        anova_df_max = anova_df.max().max()
                        self.annotate_anova_results(anova_df, sorted_categories.tolist(), use_mean=False, anova_df_max=anova_df_max)

            plt.title(f'Distribution of {col2} by {col1}')
            plt.ylabel(f'{col2}')
            plt.xlabel(col1.capitalize())
            plt.tight_layout()

        # else, indicating all data selected are numerical
        else:
            # Convert columns to numeric and drop non-numeric values
            df[col1] = pd.to_numeric(df[col1], errors='coerce')
            df[col2] = pd.to_numeric(df[col2], errors='coerce')
            if col3:
                df[col3] = pd.to_numeric(df[col3], errors='coerce')

            # Drop rows with NaN values after conversion
            df = df.dropna(subset=[col1, col2] + ([col3] if col3 else []))

            # 2 numerical variables
            if pd.api.types.is_numeric_dtype(df[col1]) and pd.api.types.is_numeric_dtype(df[col2]) and (
                    col3 is None or col3 == ""):
                var1 = df[col1]
                var2 = df[col2]
                df_plot = pd.DataFrame({
                    "Value": pd.concat([df[col1], df[col2]], ignore_index=True),
                    "Group": [col1] * len(df[col1]) + [col2] * len(df[col2])
                })

                # Sort groups by mean in descending order
                group_means = df_plot.groupby("Group")["Value"].mean().sort_values(ascending=False)
                df_plot["Group"] = pd.Categorical(df_plot["Group"], categories=group_means.index, ordered=True)

                ax = sns.violinplot(data=df_plot, x="Group", y="Value", inner="box", palette="Set2")

                if t1_bool:
                    var1_t, var1_p = stats.ttest_1samp(var1, t1_ref1)
                    var2_t, var2_p = stats.ttest_1samp(var2, t1_ref2)

                    ylim = ax.get_ylim()
                    y_star = ylim[1] + (ylim[1] - ylim[0]) * 0.005
                    y_pval = ylim[1] + (ylim[1] - ylim[0]) * 0.0025

                    ax.text(0, y_star, self.p_val_mark(var1_p), ha="center", va="bottom", fontsize=12)
                    ax.text(1, y_star, self.p_val_mark(var2_p), ha="center", va="bottom", fontsize=12)

                    ax.text(0, y_pval, f"P: {var1_p:.2e}", ha="center", va="bottom", fontsize=10)
                    ax.text(1, y_pval, f"P: {var2_p:.2e}", ha="center", va="bottom", fontsize=10)

                    ax.set_ylim(ylim[0], y_star + (ylim[1] - ylim[0]) * 0.025)

                if t2_bool:
                    t_stat, p_value = stats.ttest_ind(var1, var2)

                    ylim = ax.get_ylim()
                    bar_y = ylim[1] + (ylim[1] - ylim[0]) * 0.05

                    ax.plot([0, 1], [bar_y, bar_y], color="black", lw=1, zorder=10)
                    ax.annotate(self.p_val_mark(p_value), xy=(0.5, bar_y + (ylim[1] - ylim[0]) * 0.05), ha="center",
                                fontsize=12, color="black")
                    ax.annotate(f"p = {p_value:.2e}", xy=(0.5, bar_y + (ylim[1] - ylim[0]) * 0.02), ha="center",
                                fontsize=12, color="black")

                    ax.set_ylim(ylim[0], bar_y + (ylim[1] - ylim[0]) * 0.1)

            # 3 numerical variables
            elif pd.api.types.is_numeric_dtype(df[col1]) and pd.api.types.is_numeric_dtype(
                    df[col2]) and pd.api.types.is_numeric_dtype(df[col3]):
                df_plot = pd.DataFrame({
                    "Value": pd.concat([df[col1], df[col2], df[col3]], ignore_index=True),
                    "Group": [col1] * len(df[col1]) + [col2] * len(df[col2]) + [col3] * len(df[col3])
                })

                # Sort groups by mean in descending order
                group_means = df_plot.groupby("Group")["Value"].mean().sort_values(ascending=False)
                df_plot["Group"] = pd.Categorical(df_plot["Group"], categories=group_means.index, ordered=True)

                ax = sns.violinplot(data=df_plot, x="Group", y="Value", inner="box", palette="Set2")

                if anova_bool:
                    sorted_groups = group_means.index.tolist()
                    df_max = df_plot["Value"].max()  # Get the maximum value from the DataFrame
                    self.annotate_anova_results(df, sorted_groups, use_mean=False, anova_df_max=df_max)
                        

    def plot_box(self, df, col1, col2):
        sns.boxplot(x=df[col1], y=df[col2], showfliers=self.show_outliers)

    def plot_hist(self, df, col1):
        sns.histplot(df[col1], bins=self.bin_size, kde=self.kde_bool)

        # Add horizontal guidelines based on y-axis tick marks
        y_ticks = plt.gca().get_yticks()
        for y in y_ticks:
            plt.axhline(y=y, color='gray', linestyle='--', linewidth=0.5, alpha=0.7)

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

    def round_num(self, num):
        if num < 0.001 or num > 1000:
            return f"{num:.2e}"
        else:
            return f"{num:.2f}"

    def annotate_anova_results(self, df, variables, use_mean=True, anova_df_max=None):
        """
        Annotates ANOVA results and Tukey HSD pairwise comparisons on a bar or violin plot.

        Args:
            df (pd.DataFrame): Wide-format DataFrame with one column per group.
            variables (list): Pre-sorted list of column names in plotted x-axis order.
            use_mean (bool): Whether to use mean() to estimate vertical position (True) or provided anova_df_max (False).
            anova_df_max (float): Max y value from original unfiltered DataFrame (used when use_mean=False).
        """
        from statsmodels.stats.multicomp import pairwise_tukeyhsd

        # Stack data into long format
        df_plot = pd.DataFrame({
            "Value": pd.concat([df[var] for var in variables], ignore_index=True),
            "Group": sum([[var] * len(df[var]) for var in variables], [])
        })

        # Perform ANOVA
        anova_result = stats.f_oneway(*[df[var] for var in variables])
        print("ANOVA p-value:", anova_result.pvalue)

        # Tukey HSD
        tukey = pairwise_tukeyhsd(df_plot["Value"], df_plot["Group"], alpha=0.05)
        summary_data = tukey.summary().data[1:]  # skip header

        # Build index map from label to plotting x-axis index
        label_to_idx = {label: idx for idx, label in enumerate(variables)}

        # Annotate each pairwise comparison
        for idx, row in enumerate(summary_data):
            cat1, cat2, _, p_val = row[:4]
            i = label_to_idx[cat1]
            j = label_to_idx[cat2]

            # Determine y-position for bar based on max data value
            base = max([df[var].mean() for var in variables]) if use_mean else anova_df_max
            offset = 0.065 * (idx + 1)
            height = base * (1 + offset)

            # Draw significance bars and p-value text
            plt.plot([i, i, j, j], [height, height + 0.01 * base, height + 0.01 * base, height], color="black", lw=1, zorder=10)
            plt.plot([i, j], [height + 0.01 * base, height + 0.01 * base], color="black", lw=1, zorder=10)
            plt.annotate(f"{self.p_val_mark(p_val)} p = {p_val:.3e}", 
                         xy=((i + j) / 2, height + 0.025 * base), 
                         ha="center", fontsize=12, color="black")


    def annotate_t_test_results(self, var1, var2, t1_bool, t2_bool, t1_ref1, t1_ref2, t2_p, use_mean=True):
        """
        Annotates t-test results on a bar plot.

        Args:
            var1 (pd.Series): Data for the first variable.
            var2 (pd.Series): Data for the second variable.
            t1_bool (bool): Whether to perform and annotate one-sample t-tests.
            t2_bool (bool): Whether to perform and annotate two-sample t-tests.
            t1_ref1 (float): Reference value for the one-sample t-test for var1.
            t1_ref2 (float): Reference value for the one-sample t-test for var2.
            t2_p (float): P-value for the two-sample t-test.
            use_mean (bool): Whether to use mean() to calculate two_bar_y. If False, use max().
        """
        two_bar_y = max(var1.max(), var2.max()) if not use_mean else max(var1.mean(), var2.mean())

        if t1_bool:
            _, var1_p = stats.ttest_1samp(var1, t1_ref1)
            _, var2_p = stats.ttest_1samp(var2, t1_ref2)

            # Annotate one-sample t-test results with dynamic spacing
            spacing_factor = 0.03 + 0.02 * (
                var1.mean() / var2.mean() if var1.mean() > var2.mean() else var2.mean() / var1.mean())
            plt.text(0, var1.mean() * (1 + spacing_factor), self.p_val_mark(var1_p), ha="center", va="bottom",
                     fontsize=14)
            plt.text(1, var2.mean() * (1 + spacing_factor), self.p_val_mark(var2_p), ha="center", va="bottom",
                     fontsize=14)

            plt.text(0, var1.mean() * (1 + spacing_factor / 2), f"P: {self.round_num(var1_p)}", ha="center",
                     va="bottom", fontsize=12)
            plt.text(1, var2.mean() * (1 + spacing_factor / 2), f"P: {self.round_num(var2_p)}", ha="center",
                     va="bottom", fontsize=12)

        if t2_bool:
            # Annotate two-sample t-test results
            two_bar_y *= 1.1
            plt.plot([0, 0, 1, 1], [two_bar_y, two_bar_y * 1.003, two_bar_y * 1.003, two_bar_y], lw=1.5, color='black')
            plt.text(0.5, two_bar_y * 1.03, self.p_val_mark(t2_p), ha="center", va="bottom", fontsize=14)
            plt.text(0.5, two_bar_y * 1.01, f"P: {self.round_num(t2_p)}", ha="center", va="bottom", fontsize=12)

        # Adjust y-axis limit
        plt.ylim(0, two_bar_y * 1.1)

    def pairplot(self, df, numeric_columns):
        """
        Generates a pairplot for user-specified or all numerical variables in the dataset.

        Parameters:
        - df: pandas DataFrame containing the dataset.
        - numeric_columns: List of numerical column names to include in the pairplot.
        """
        # Use user-specified variables if provided
        if hasattr(self, 'pairplot_variables') and self.pairplot_variables.strip():
            user_variables = [var.strip() for var in self.pairplot_variables.split(",")]
            # Validate that the variables exist in the dataset
            valid_variables = [var for var in user_variables if var in numeric_columns]
            if not valid_variables:
                raise ValueError("No valid numerical variables specified for pairplot.")
        else:
            valid_variables = numeric_columns

        # Generate the pairplot
        sns.pairplot(df[valid_variables])
        plt.suptitle("Pairplot of Selected Variables", y=1.02)  # Add a title
        plt.show()