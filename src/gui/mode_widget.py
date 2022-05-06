from tkinter import *
from tkinter import ttk

class tkMode_Widget:
    def __init__(self, parent, mode: StringVar, output: BooleanVar):
        self.mainframe = ttk.Frame(parent, padding="3 3 12 12",
                        borderwidth=2, relief='solid')
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S)) 
        self.mode = mode
        self.output = output

        #Define Widgets
        lbl_title = ttk.Label(self.mainframe, text="Model View")
        lbl_title.grid(column=0, row=0, columnspan=4)

        self.bt_shade = ttk.Button(self.mainframe, text='Shaded', command=self.setShade, state=['disabled'])
        self.bt_shade.grid(column=0, row=1, sticky=E)

        self.bt_wire = ttk.Button(self.mainframe, text='Wireframe', command=self.setWire)
        self.bt_wire.grid(column=1, row=1, sticky=E)
        
        self.bt_slice = ttk.Button(self.mainframe, text='Slice', command=self.setSlice)
        self.bt_slice.grid(column=2, row=1, sticky=E)

        self.bt_paths = ttk.Button(self.mainframe, text='Paths', command=self.setPaths)
        self.bt_paths.grid(column=3, row=1, sticky=E)

        self.bt_output = ttk.Button(self.mainframe, text="Output Path File", command=self.createOutput)
        self.bt_output.grid(column=2, row=2, sticky=E, columnspan=2)
        self.bt_output.state(['disabled'])
        
    def setShade(self):
        self.mode.set('shade')
        self.setButtonStates(shade=False)

    def setWire(self):
        self.mode.set('wire')
        self.setButtonStates(wire=False)

    def setSlice(self):
        self.mode.set('slice')
        self.setButtonStates(slice=True)

    def setPaths(self):
        self.mode.set('paths')
        self.setButtonStates(paths=True)

    def createOutput(self):
        self.output.set(bool(True))

    def setButtonStates(self, shade=True, wire=True, slice=True, paths=True):
        self.bt_shade.state(['!disabled']) if shade else self.bt_shade.state(['disabled'])
        self.bt_wire.state(['!disabled']) if wire else self.bt_wire.state(['disabled'])
        self.bt_slice.state(['!disabled']) if slice else self.bt_slice.state(['disabled'])
        self.bt_paths.state(['!disabled']) if paths else self.bt_paths.state(['disabled'])
        self.bt_output.state(['!disabled']) if paths else self.bt_paths.state(['disabled'])
