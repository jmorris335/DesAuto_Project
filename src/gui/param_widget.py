from tkinter import *
from tkinter import ttk

class tkParam_Widget:
    def __init__(self, parent, layer_height: StringVar, wall_thickness: StringVar, 
                density: StringVar, layer_index: StringVar):
        self.mainframe = ttk.Frame(parent, padding="3 3 12 12",
                        borderwidth=2, relief='solid')
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S)) 
        self.lh = layer_height
        self.wall = wall_thickness
        self.dens = density
        self.l_index = layer_index

        #Define Widgets
        lbl_title = ttk.Label(self.mainframe, text="Parameters")
        lbl_title.grid(column=0, row=0, columnspan=4)

        lbl_lh = ttk.Label(self.mainframe, text="Layer Height: ")
        lbl_lh.grid(column=0, row=1)

        entry_lh = ttk.Entry(self.mainframe, textvariable=self.lh, width=5)
        entry_lh.grid(column=1, row=1)

        lbl_wall = ttk.Label(self.mainframe, text="Wall Thickness: ")
        lbl_wall.grid(column=2, row=1)

        entry_wall = ttk.Entry(self.mainframe, textvariable=self.wall, width=5)
        entry_wall.grid(column=3, row=1)

        lbl_dens = ttk.Label(self.mainframe, text="Infill Density: ")
        lbl_dens.grid(column=0, row=2)

        entry_dens = ttk.Entry(self.mainframe, textvariable=self.dens, width=5)
        entry_dens.grid(column=1, row=2)

        lbl_l_ind = ttk.Label(self.mainframe, text="Layer Index: ")
        lbl_l_ind.grid(column=2, row=2)

        entry_l_ind = ttk.Entry(self.mainframe, textvariable=self.l_index, width=5)
        entry_l_ind.grid(column=3, row=2)      
