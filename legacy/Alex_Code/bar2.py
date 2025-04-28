import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from tkinter import filedialog, messagebox, ttk

path="C:/Users/Alex/Downloads/country_vaccinations.csv"
data=pd.read_csv(path)
#print(data.head())

input_cat="Mexico, United States, Canada"
col1 = "country"
col2 = "daily_vaccinations_per_million"


def plot_bar_num_cat (df, col1, col2, input_cat):
    # Normalize user input
    input_list_raw = [item.strip() for item in input_cat.split(",")]
    input_list_lower = [item.lower() for item in input_list_raw]

    # Clean and lowercase column values for filtering
    df[col1] = df[col1].astype(str).str.strip()
    df['__lower_temp__'] = df[col1].str.lower()

    # Filter using lowercase match
    filtered_df = df[df['__lower_temp__'].isin(input_list_lower)]

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
    plt.show()
    

plot_bar_num_cat(data, col1, col2, input_cat)