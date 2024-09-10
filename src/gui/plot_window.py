from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image
import os

from src.gui.ortho_widget import tkOrtho_Widget
from src.gui.translate_widget import tkTranslate_Widget
from src.gui.rotation_widget import tkRotate_Widget
from src.gui.mode_widget import tkMode_Widget
from src.gui.param_widget import tkParam_Widget
from src.gui.alignment_widget import tkAlign_Widget
from src.gui.zoom_widget import tkZoom_Widget
from src.gui.pan_widget import tkPan_Widget
from src.gui.scale_widget import tkScale_Widget

from src.STL.ReadSTL import STL
from src.STL.PlotSTL import PlotSTL

class tkSTL_Plot:
    def __init__(self, stl: STL, parent): 
        self.mainframe = ttk.Frame(parent, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))  
        self.stl = stl
        self.plotter = PlotSTL(stl)

        # Define Strings 
        self.lbl_mode = StringVar(value='shade') 
        self.lbl_mode.trace_add('write', self.plot) 
        self.lbl_output = BooleanVar(value='False')
        self.lbl_output.trace_add('write', self.createOutput)

        self.lbl_translate_step = StringVar(value='5')
        self.lbl_translate_dir = StringVar()
        self.lbl_translate_dir.trace_add('write', self.defineTranslate)

        self.lbl_rotate_step = StringVar(value=45)
        self.lbl_rotate_dir = StringVar()
        self.lbl_rotate_dir.trace_add('write', self.defineRotate)

        self.lbl_ortho = StringVar()
        self.lbl_ortho.trace_add('write', self.defineOrtho)

        self.lbl_scaling = StringVar(value='0.0')
        self.lbl_scaling.trace_add('write', self.defineScaling)

        self.lbl_lh = StringVar(value='.5')
        self.lbl_wall = StringVar(value='1.5')
        self.lbl_dens = StringVar(value='0.2')

        self.lbl_align_view = StringVar(value='original')
        self.lbl_align_view.trace_add('write', self.defineAlignment)
        self.lbl_align_azim = StringVar(value='0')
        self.lbl_align_elev = StringVar(value='90')

        self.lbl_layer = StringVar(value='1000')
        self.lbl_layer.trace_add('write', self.plot)

        self.lbl_zoom = IntVar(value=100)
        self.lbl_zoom.trace_add('write', self.setZoom)

        self.lbl_pan_x = IntVar(value=0)
        self.lbl_pan_x.trace_add('write', self.definePan)
        self.lbl_pan_y = IntVar(value=0)
        self.lbl_pan_y.trace_add('write', self.definePan)
        self.lbl_pan_z = IntVar(value=0)
        self.lbl_pan_z.trace_add('write', self.definePan)
        self.lbl_pan_reset = BooleanVar(value=False)
        self.lbl_pan_reset.trace_add('write', self.resetPlot)

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

        set_scaling = ttk.Frame(self.mainframe, padding="3 3 5 5")
        set_scaling.grid(column=2, row=5, sticky=W)
        self.widget_scaling = tkScale_Widget(set_scaling, self.lbl_scaling)

        set_mode = ttk.Frame(self.mainframe, padding="3 3 0 0")
        set_mode.grid(column=0, row=0, sticky=(S), columnspan=2)
        tkMode_Widget(set_mode, self.lbl_mode, self.lbl_output)

        set_param = ttk.Frame(self.mainframe, padding="3 3 0 0")
        set_param.grid(column=2, row=0, sticky=W)
        tkParam_Widget(set_param, self.lbl_lh, self.lbl_wall, self.lbl_dens, self.lbl_layer)

        set_pan = ttk.Frame(self.mainframe, padding="3 3 0 0")
        set_pan.grid(column=0, row=5, sticky=N)
        tkPan_Widget(set_pan, self.lbl_pan_x, self.lbl_pan_y, self.lbl_pan_z, self.lbl_pan_reset)
        
        # Make Plot Canvas
        self.plotter.fitToBuildSpace()
        self.plotter.plotSTL(False)
        plot_img = self.getImage(self.plotter.fig)
        self.canvas = Canvas(self.mainframe, width=plot_img.width()+26, height=plot_img.height())
        self.canvas.grid(column=0, row=1, sticky=(N, S, E, W), rowspan=4, columnspan=2) 
        self.img_container = self.canvas.create_image(0, 0, image=plot_img, anchor='nw')

        self.scale_zoom = tkZoom_Widget(self.canvas, self.lbl_zoom)
        self.scale_zoom.place(x=plot_img.width(), y=6)

    def plot(self, *args):
        ''' Refreshes the plot according to the inputted mode.'''
        self.plotter.clearPlot()
        mode = self.lbl_mode.get()
        if mode == 'shade':
            self.plotter.plotSTL(False)
        elif mode == 'wire':
            self.plotter.plotWireframe(False)
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
        self.setZoom(toPlot=False)
        self.definePan(toPlot=False)
        self.updateImage()

    def updateImage(self):
        ''' Updates image.'''
        plot_img = self.getImage(self.plotter.fig)
        self.canvas.itemconfig(self.img_container, image=plot_img)

    def getImage(self, fig, filename='curr_plot.png'):
        ''' Saves and returns the image of the plot.'''
        cur_path = os.path.dirname(__file__)
        filepath = os.path.join(cur_path, '..', filename)
        fig.savefig(filepath, bbox_inches='tight', pad_inches=-.2)
        global plot_img
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
                elif dir == 'floor': self.plotter.moveToFloor()
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

    def setZoom(self, *args, toPlot=True):
        try:
            level = self.lbl_zoom.get()
            if level <= 100 and level >= 0:
                self.plotter.zoomRegular(100-level, 1.)
            if toPlot: self.plot()
        except Exception as e: print(e)

    def definePan(self, *args, toPlot=True):
        try:
            pan_x = int(self.lbl_pan_x.get())
            pan_y = int(self.lbl_pan_y.get())
            pan_z = int(self.lbl_pan_z.get())
            self.plotter.panRegular(pan_x, pan_y, pan_z)
            if toPlot: self.plot()
        except Exception as e: print(e)

    def resetPlot(self, *args):
        try:
            self.lbl_ortho.set('front')
            self.lbl_align_view.set('original')
            self.widget_scaling.scl_scale.set(1)
            self.plotter.resetScale()
            self.plotter.updateSTL()
            self.scale_zoom.scl_zoom.set(100)
        except Exception as e: print(e)

    def defineScaling(self, *args):
        try:
            level = float(self.lbl_scaling.get())
            if level < 1 and level > -1: return
            elif level <= 5 and level >= 0:
                self.plotter.scale(level)
            elif level < 0:
                self.plotter.scale(1/abs(level))
            self.plotter.updateSTL()
            self.plot()
        except Exception as e: print(e)

    def createOutput(self, *args):
        self.plotter.savePaths()
        cur_path = os.path.dirname(__file__)
        og_filepath = os.path.join(cur_path, '..', 'curr_paths.txt')
        new_filepath = filedialog.asksaveasfilename()
        os.rename(og_filepath, new_filepath)
