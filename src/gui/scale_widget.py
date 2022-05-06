from tkinter import *
from tkinter import ttk

class tkScale_Widget:
    def __init__(self, parent, level: StringVar):
        self.mainframe = ttk.Frame(parent, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S)) 
        self.level = level
        self.txt_factor = StringVar(value='1')
        self.scale_at = DoubleVar(value=0.0)

        #Define Widgets
        lbl_title = ttk.Label(self.mainframe, text="Scale Model")
        lbl_title.grid(column=0, row=0, columnspan=2, sticky=(N, S))

        self.scl_scale = ttk.Scale(self.mainframe, orient=HORIZONTAL, length=250, 
            from_=-5., to=5., command=self.setScale, variable=self.scale_at)
        self.scl_scale.grid(column=0, row=1,sticky=(N, W, E, S))

        b = ttk.Button(self.mainframe, text='Scale', command=self.goScale)
        b.grid(column=1, row=1, sticky=(N, W))

        lbl_value = ttk.Label(self.mainframe, textvariable=self.txt_factor)
        lbl_value.grid(column=0, row=2, sticky=(N))

    def setScale(self, val):
        value = float(val)
        if value < 1 and value > -1:
            self.txt_factor.set('1')
        else: self.txt_factor.set(str(value))

    def goScale(self, *args):
        value = self.scale_at.get()
        if value < 1 and value > -1:
            self.level.set(str('1'))
        else:
            self.level.set(str(value))

    def place(self, **kwargs):
        self.scl_zoom.place(kwargs)
