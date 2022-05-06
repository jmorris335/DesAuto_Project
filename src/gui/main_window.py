from tkinter import *
from tkinter import ttk
from tkinter import filedialog

from src.gui.plot_window import tkSTL_Plot

from src.STL.ReadSTL import STL

class Main:
    def __init__(self, root):
        root.title("Slicer Team 6")

        self.mainframe = ttk.Frame(root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        #Define variables
        self.file_path = StringVar()
        self.file_path.trace_add('write', self.makePlot)

        #Define Widgets
        ttk.Button(self.mainframe, text="Select File", command=self.getFile).grid(column=0, row=2, sticky=W)

        #Operational Footer
        for child in self.mainframe.winfo_children(): 
            child.grid_configure(padx=5, pady=5)
        root.bind("<Return>", self.getFile)

    def getFile(self, *args):
        try:
            self.file_path.set(filedialog.askopenfilename())
        except ValueError:
            pass    

    def makePlot(self, *args):
        plotFrame = ttk.Frame(self.mainframe, padding="10 10 20 20")
        plotFrame.grid(column=0, row=1)
        if self.file_path.get() != '':
            stl = STL(self.file_path.get())
            plot = tkSTL_Plot(stl, plotFrame)