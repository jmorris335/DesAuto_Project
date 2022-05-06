from tkinter import *
from tkinter import ttk

class tkTranslate_Widget:
    def __init__(self, parent, step: StringVar, dir: StringVar):
        self.mainframe = ttk.Frame(parent, padding="3 3 12 12",
                        borderwidth=2, relief='solid')
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S)) 
        self.step = step
        self.dir = dir

        #Define Widgets
        lbl_title = ttk.Label(self.mainframe, text="Translate Model")
        lbl_title.grid(column=0, row=0, columnspan=3)

        lbl_step = ttk.Label(self.mainframe, text="Displacement: ")
        lbl_step.grid(column=0, row=1)

        entry_step = ttk.Entry(self.mainframe, textvariable=self.step, width=5)
        entry_step.grid(column=1, row=1)

        bt_up = ttk.Button(self.mainframe, text='Up', command=self.setUp)
        bt_up.grid(column=1, row=2, sticky=(N,S,E,W))
        
        bt_left = ttk.Button(self.mainframe, text='Left', command=self.setLeft)
        bt_left.grid(column=0, row=3, sticky=(N,S,E,W))
        
        bt_right = ttk.Button(self.mainframe, text='Right', command=self.setRight)
        bt_right.grid(column=2, row=3, sticky=(N,S,E,W))
        
        bt_down = ttk.Button(self.mainframe, text='Down', command=self.setDown)
        bt_down.grid(column=1, row=4, sticky=(N,S,E,W))
        
    def setUp(self):
        self.dir.set('up')

    def setRight(self):
        self.dir.set('right')

    def setLeft(self):
        self.dir.set('left')

    def setDown(self):
        self.dir.set('down')
