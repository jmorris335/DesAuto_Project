from tkinter import *
from tkinter import ttk

class tkZoom_Widget:
    def __init__(self, parent, level: IntVar):
        self.level = level

        #Define Widgets
        self.scl_zoom = ttk.Scale(parent, orient=VERTICAL, length=200, 
                    from_=0., to=100., command=self.setZoom, value=100)
        self.scl_zoom.grid(column=0, row=0, sticky=(N, W, E, S))

    def setZoom(self, val):
        value = int(float(val))
        level = self.level.get()
        if value != level:
            self.level.set(value)

    def place(self, **kwargs):
        self.scl_zoom.place(kwargs)
