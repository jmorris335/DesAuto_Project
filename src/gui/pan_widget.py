from tkinter import *
from tkinter import ttk

class tkPan_Widget:
    def __init__(self, parent, xPan: IntVar, yPan: IntVar, zPan: IntVar, reset: BooleanVar):
        self.mainframe = ttk.Frame(parent, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S)) 
        self.xPan = xPan
        self.yPan = yPan
        self.zPan = zPan
        self.reset = reset

        #Define Widgets
        lbl_title = ttk.Label(self.mainframe, text="Pan")
        lbl_title.grid(column=0, row=0, columnspan=3)

        lbl_xPan = ttk.Label(self.mainframe, text="X Direction")
        lbl_xPan.grid(column=0, row=1)

        self.scl_xPan = ttk.Scale(self.mainframe, orient=HORIZONTAL, length=300, 
                    from_=-10., to=10., command=self.setXPan, value=0)
        self.scl_xPan.grid(column=1, row=1, sticky=(N, W, E, S))

        lbl_yPan = ttk.Label(self.mainframe, text="Y Direction")
        lbl_yPan.grid(column=0, row=2)

        self.scl_yPan = ttk.Scale(self.mainframe, orient=HORIZONTAL, length=300, 
                    from_=-10., to=10., command=self.setYPan, value=0)
        self.scl_yPan.grid(column=1, row=2, sticky=(N, W, E, S))

        lbl_zPan = ttk.Label(self.mainframe, text="Z Direction")
        lbl_zPan.grid(column=0, row=3)

        self.scl_zPan = ttk.Scale(self.mainframe, orient=HORIZONTAL, length=300, 
                    from_=-10., to=10., command=self.setZPan, value=0)
        self.scl_zPan.grid(column=1, row=3, sticky=(N, W, E, S))

        self.b = ttk.Button(self.mainframe, text='Reset', width=5, command=self.callReset)
        self.b.grid(column=3, row=1, rowspan=3, sticky=(N,S,E))

    def setXPan(self, val):
        value = int(float(val))
        level = self.xPan.get()
        if value != level:
            self.xPan.set(value)

    def setYPan(self, val):
        value = int(float(val))
        level = self.yPan.get()
        if value != level:
            self.yPan.set(value)

    def setZPan(self, val):
        value = int(float(val))
        level = self.zPan.get()
        if value != level:
            self.zPan.set(value)

    def callReset(self, *args):
        self.scl_xPan.set(0)
        self.scl_yPan.set(0)
        self.scl_zPan.set(0)
        val = bool(self.reset.get())
        val = not val
        self.reset.set(val)

    def place(self, **kwargs):
        self.mainframe.place(kwargs)
