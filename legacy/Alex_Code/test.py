from plotter import Plotter
import pandas as pd
import matplotlib.pyplot as plt

path="C:/Users/Alex/Downloads/Cancer_Data.csv"
data =pd.read_csv(path)
x = data["diagnosis"]
y = data["radius_mean"]


plt.bar(x,y)
plt.show()

'''
x = ['Apple', 'Banana', 'Cherry', 'Date']
y = [23, 17, 35, 29]

x_res = 1280
y_res = 720

plotter= Plotter(x_res=x_res, y_res=y_res)

plotter.bar_plot(x, y)
'''