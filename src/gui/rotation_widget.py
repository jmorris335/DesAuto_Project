from tkinter import *
from tkinter import ttk

class tkRotate_Widget:
    def __init__(self, parent, step: StringVar, dir: StringVar):
        self.mainframe = ttk.Frame(parent, padding="3 3 12 12",
                        borderwidth=2, relief='solid')
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S)) 
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        self.step = step
        self.dir = dir

        #Define Widgets
        lbl_title = ttk.Label(self.mainframe, text="Rotate Model")
        lbl_title.grid(column=0, row=0, columnspan=3)

        lbl_step = ttk.Label(self.mainframe, text="Angle: ")
        lbl_step.grid(column=0, row=1)

        entry_step = ttk.Entry(self.mainframe, textvariable=self.step, width=5)
        entry_step.grid(column=1, row=1)

        bt_up = ttk.Button(self.mainframe, text='Theta', command=self.setTheta)
        bt_up.grid(column=0, row=2, sticky=(N,S,E,W))
        
        bt_left = ttk.Button(self.mainframe, text='Phi', command=self.setPhi)
        bt_left.grid(column=1, row=2, sticky=(N,S,E,W))
        
        bt_right = ttk.Button(self.mainframe, text='Psi', command=self.setPsi)
        bt_right.grid(column=2, row=2, sticky=(N,S,E,W))
        
    def setTheta(self):
        self.dir.set('theta')

    def setPhi(self):
        self.dir.set('phi')

    def setPsi(self):
        self.dir.set('psi')
