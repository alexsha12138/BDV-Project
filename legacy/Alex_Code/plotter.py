import matplotlib.pyplot as plt
import pandas as pd

class Plotter:
    def __init__(self, x_res, y_res, dpi=100):
        self.x_res=x_res
        self.y_res=y_res
        self.dpi=dpi
        self.width=x_res/dpi
        self.height=y_res/dpi

    def _setup_figure(self):
         plt.figure(figsize=(self.width, self.height), dpi=self.dpi)

    def bar_plot(self, x_var, y_var, title = "Title", xlabel="x aixs", ylabel = "y axis"):
        self._setup_figure()

        if hasattr(x_var, "dtype") and hasattr(y_var, "dtype"):
            # combine two variables into a data frame
            df = pd.DataFrame({"x": x_var, "y": y_var})
            grouped=df.groupby("x")["y"].mean()
            x_data= grouped.index
            y_data = grouped.values
        else:
            x_data = x_var
            y_data = y_var

        plt.bar(x_data, y_data)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        plt.tight_layout()
        plt.show()
