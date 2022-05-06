from src.gui.main_window import Main

from tkinter import *
from tkinter import ttk

def main():
    ''' Main caller for GUI and Slicer'''
    root = Tk()
    Main(root)
    root.mainloop()

if __name__ == '__main__':
    main()