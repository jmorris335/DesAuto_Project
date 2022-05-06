from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
from os import path

from gui.ortho_widget import tkOrtho_Widget
from gui.translate_widget import tkTranslate_Widget
from gui.rotation_widget import tkRotate_Widget
from gui.mode_widget import tkMode_Widget
from gui.param_widget import tkParam_Widget
from gui.alignment_widget import tkAlign_Widget

from STL.ReadSTL import STL
from STL.PlotSTL import PlotSTL

class tkSTL_Plot:
    def __init__(self, stl: STL, parent): 
        self.mainframe = ttk.Frame(parent, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))  
        self.stl = stl
        self.plotter = PlotSTL(stl)

        # Define Strings 
        self.lbl_mode = StringVar(value='shade') 
        self.lbl_mode.trace_add('write', self.plot) 

        self.lbl_translate_step = StringVar(value='5')
        self.lbl_translate_dir = StringVar()
        self.lbl_translate_dir.trace_add('write', self.defineTranslate)

        self.lbl_rotate_step = StringVar(value=45)
        self.lbl_rotate_dir = StringVar()
        self.lbl_rotate_dir.trace_add('write', self.defineRotate)

        self.lbl_ortho = StringVar()
        self.lbl_ortho.trace_add('write', self.defineOrtho)

        self.lbl_lh = StringVar(value='.5')
        self.lbl_wall = StringVar(value='1.5')
        self.lbl_dens = StringVar(value='0.2')

        self.lbl_align_view = StringVar(value='original')
        self.lbl_align_view.trace_add('write', self.defineAlignment)
        self.lbl_align_azim = StringVar(value='0')
        self.lbl_align_elev = StringVar(value='90')

        self.lbl_layer = StringVar(value=1000)

        # Make Widgets
        set_translate = ttk.Frame(self.mainframe, padding="3 3 5 5")
        set_translate.grid(column=2, row=1, sticky=W)
        tkTranslate_Widget(set_translate, self.lbl_translate_step, self.lbl_translate_dir)

        set_rotate = ttk.Frame(self.mainframe, padding="3 3 5 5")
        set_rotate.grid(column=2, row=2, sticky=W)
        tkRotate_Widget(set_rotate, self.lbl_rotate_step, self.lbl_rotate_dir)
        
        set_ortho = ttk.Frame(self.mainframe, padding="3 3 5 5")
        set_ortho.grid(column=2, row=3, sticky=W)
        tkOrtho_Widget(set_ortho, self.lbl_ortho)

        set_align = ttk.Frame(self.mainframe, padding="3 3 5 5")
        set_align.grid(column=2, row=4, sticky=W)
        tkAlign_Widget(set_align, self.lbl_align_view, self.lbl_align_azim, self.lbl_align_elev)

        set_mode = ttk.Frame(self.mainframe, padding="3 3 0 0")
        set_mode.grid(column=0, row=0, sticky=W, columnspan=2)
        tkMode_Widget(set_mode, self.lbl_mode)

        set_param = ttk.Frame(self.mainframe, padding="3 3 0 0")
        set_param.grid(column=2, row=0, sticky=W)
        tkParam_Widget(set_param, self.lbl_lh, self.lbl_wall, self.lbl_dens, self.lbl_layer)

        # Perform Actions
        self.plotter.plotSTL(False)
        plot_img = self.getImage(self.plotter.fig)
        self.canvas = Canvas(self.mainframe, width=plot_img.width(), height=plot_img.height())
        self.canvas.grid(column=0, row=1, sticky=(N, S, E, W), rowspan=4, columnspan=2) 
        self.img_container = self.canvas.create_image(0, 0, image=plot_img, anchor='nw')

    def plot(self, *args):
        ''' Refreshes the plot according to the inputted mode.'''
        self.plotter.clearPlot()
        mode = self.lbl_mode.get()
        if mode == 'shade' or mode == 'wire':
            self.plotter.plotSTL(False)
        elif mode == 'slice': 
            layer_ht = float(self.lbl_lh.get())
            layer = int(self.lbl_layer.get())
            self.plotter.slice(layer_ht)
            self.plotter.highlightLayer(layer)
        elif mode == 'paths': 
            layer_ht = float(self.lbl_lh.get())
            wall_t = float(self.lbl_wall.get())
            density = float(self.lbl_dens.get())
            layer = int(self.lbl_layer.get())
            self.plotter.buildExtrusion(wall_t, layer_ht, density)
            self.plotter.plotExtrudedUptoLayer(layer)
        self.updateImage()

    def updateImage(self):
        ''' Updates image.'''
        plot_img = self.getImage(self.plotter.fig)
        self.canvas.itemconfig(self.img_container, image=plot_img)

    def getImage(self, fig, filename='curr_plot.png'):
        ''' Saves and returns the image of the plot.'''
        cur_path = path.dirname(__file__)
        filepath = path.join(cur_path, '..', filename)
        fig.savefig(filepath, bbox_inches='tight', pad_inches=-.2)
        plot_img = ImageTk.PhotoImage(Image.open(filepath))
        return plot_img

    def defineOrtho(self, *args):
        ''' Orients the part to an orthographic view (where front is defined as the
        orientation of the part when it was initially loaded). 
        
        Inputs
        ---
        view : str ("front", "back", "right", "left", "top", "bottom")
            The view to rotate to. If the input is not one of the specified values
            the function prints a warning message to the screen but otherwise makes
            no action.
        '''
        try:
            ortho = self.lbl_ortho.get()
            if ortho != '':
                self.plotter.orthographic(ortho)
                self.plotter.updateSTL()
                self.plot()
        except Exception as e: print(e)

    def defineTranslate(self, *args):
        try:
            dir = self.lbl_translate_dir.get()
            step = float(self.lbl_translate_step.get())
            if dir != '':
                delx = 0
                dely = 0
                if dir == 'left': delx = -step
                elif dir == 'right': delx = step
                elif dir == 'up': dely = step
                elif dir == 'down': dely = -step
                self.plotter.translate(delx=delx, dely=dely)
                self.plotter.updateSTL()
                self.plot()
        except Exception as e: print(e)

    def defineRotate(self, *args):
        try:
            dir = self.lbl_rotate_dir.get()
            step = float(self.lbl_rotate_step.get())
            if dir != '':
                delth = 0
                delph = 0
                delps = 0
                if dir == 'theta': delth = step
                elif dir == 'phi': delph = step
                elif dir == 'psi': delps = step
                self.plotter.rotate(theta=delth, phi=delph, psi=delps)
                self.plotter.updateSTL()
                self.plot()
        except Exception as e: print(e)

    def defineAlignment(self, *args):
        try:
            view = self.lbl_align_view.get()
            azim = float(self.lbl_align_azim.get())
            elev = float(self.lbl_align_elev.get())
            if view == 'top': self.plotter.alignXY()
            elif view == 'front': self.plotter.align(elev=0, azim=270)
            elif view == 'original': self.plotter.align(elev=30, azim=-60)
            elif view == 'custom': self.plotter.align(elev=elev, azim=azim)
            
            if view != '':
                self.plot()
        except Exception as e: print(e)
