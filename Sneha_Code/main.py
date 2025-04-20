import tkinter as tk
from GUI import CSVPlotterApp

def main():
    root = tk.Tk()
    app = CSVPlotterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()