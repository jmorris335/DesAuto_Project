from tkinter import *
from tkinter import ttk

class tkAlign_Widget:
    def __init__(self, parent, view: StringVar, azim: StringVar, elev: StringVar):
        self.mainframe = ttk.Frame(parent, padding="3 3 12 12",
                        borderwidth=2, relief='solid')
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S)) 
        self.view = view
        self.azim = azim
        self.elev = elev

        #Define Widgets
        lbl_title = ttk.Label(self.mainframe, text="Rotate View")
        lbl_title.grid(column=0, row=0, columnspan=4)

        bt_top = ttk.Button(self.mainframe, text='Top', command=self.setTop)
        bt_top.grid(column=0, row=1, sticky=(N,S,E,W))
        
        bt_front = ttk.Button(self.mainframe, text='Front', command=self.setFront)
        bt_front.grid(column=1, row=1, sticky=(N,S,E,W))

        bt_custom = ttk.Button(self.mainframe, text='Custom', command=self.setCustom)
        bt_custom.grid(column=2, row=1, sticky=(N,S,E,W))
        
        bt_reset = ttk.Button(self.mainframe, text='Reset', command=self.setReset)
        bt_reset.grid(column=3, row=1, sticky=(N,S,E,W))

        lbl_azim = ttk.Label(self.mainframe, text="Azimuth: ")
        lbl_azim.grid(column=0, row=2)

        entry_azim = ttk.Entry(self.mainframe, textvariable=self.azim, width=5)
        entry_azim.grid(column=1, row=2)

        lbl_elev = ttk.Label(self.mainframe, text="Elevation: ")
        lbl_elev.grid(column=2, row=2)

        entry_elev = ttk.Entry(self.mainframe, textvariable=self.elev, width=5)
        entry_elev.grid(column=3, row=2)
        
    def setTop(self):
        self.view.set('top')

    def setFront(self):
        self.view.set('front')

    def setCustom(self):
        self.view.set('custom')

    def setReset(self):
        self.view.set('original')
