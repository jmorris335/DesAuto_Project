from STL.ReadSTL import STL
from STL.PlotSTL import PlotSTL
from gui.main_window import Main

from tkinter import *
from tkinter import ttk

def main():
    root = Tk()
    Main(root)
    root.mainloop()

if __name__ == '__main__':
    main()