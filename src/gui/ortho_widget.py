from tkinter import *
from tkinter import ttk

class tkOrtho_Widget:
    def __init__(self, parent, label: StringVar):
        self.mainframe = ttk.Frame(parent, padding="3 3 12 12",
                        borderwidth=2, relief='solid')
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S)) 
        self.label = label

        #Define Widgets
        lbl_title = ttk.Label(self.mainframe, text="Orthographic Rotations")
        lbl_title.grid(column=0, row=0, columnspan=3)

        bt_top = ttk.Button(self.mainframe, text='Top', command=self.setTop)
        bt_top.grid(column=2, row=1, sticky=(N,S,E,W))
        
        bt_left = ttk.Button(self.mainframe, text='Left', command=self.setLeft)
        bt_left.grid(column=0, row=2, sticky=(N,S,E,W))
        
        bt_front = ttk.Button(self.mainframe, text='Front', command=self.setFront)
        bt_front.grid(column=0, row=1, sticky=(N,S,E,W))
        
        bt_right = ttk.Button(self.mainframe, text='Right', command=self.setRight)
        bt_right.grid(column=1, row=2, sticky=(N,S,E,W))
        
        bt_back = ttk.Button(self.mainframe, text='Back', command=self.setBack)
        bt_back.grid(column=1, row=1, sticky=(N,S,E,W))
        
        bt_bottom = ttk.Button(self.mainframe, text='Bottom', command=self.setBottom)
        bt_bottom.grid(column=2, row=2, sticky=(N,S,E,W))

    def setTop(self):
        self.label.set('top')

    def setBottom(self):
        self.label.set('bottom')

    def setLeft(self):
        self.label.set('left')

    def setFront(self):
        self.label.set('front')

    def setRight(self):
        self.label.set('right')

    def setBack(self):
        self.label.set('back')

    def setBottom(self):
        self.label.set('bottom')