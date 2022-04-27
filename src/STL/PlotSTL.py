import matplotlib.pyplot as plt
# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

from ReadSTL import STL, STL_Facet as Face
from SliceSTL import Slicer, Slice, Hull
from Transform import Transform

class PlotSTL(object):
    def __init__(self, stl: STL):
        ''' Container that handles plotting and transformations for an
        STL object.
        
        Inputs
        ---
        stl : STL
            The STL object
            
        Contents for Calling
        ---
        ### Plotting Methods (Use to plot the STL)
        1. plotSTL() : Call this to plot the STL as currently represented
        
        ### Transformation Methods (Use to transform the STL)
        1. getCentroid() : Calculates the geometric centroid of the STL (costly)
        2. rotate() : Rotates the STL
        3. translate() : Translates the STL
        4. orthograpihc() : Rotates to an orthographic view
        5. moveToFloor() : Moves the STL so the lowest point is on the zplane
        6. moveToCenter() : Centers the STL horizontally on the screen
        7. updateSTL() : MUST BE CALLED TO TRANSFORM THE STL AFTER ANOTHER
            TRANSFORMATION METHOD HAS BEEN CALLED

        Example
        ---
        ```
        stl = STL("Sample STL Files/House4 106.stl") #Load the STL
        print(stl.toString()) #Check functionally loaded
        StlPlt = PlotSTL(stl) #Create the PlotSTL object
        StlPlt.orthographic("left") #Rotate to left view of STL
        StlPlt.rotate(psi=np.pi/4) #Rotate pi/4 radians around the vertical axis
        StlPlt.moveToFloor() #Lower the STL to the floor
        StlPlt.moveToCenter() #Move the STL to the center of the build plate
        StlPlt.updateSTL() #Load all transformations
        StlPlt.plotSTL() #Plot the STL to the screen
        ```
        '''
        self.stl = stl
        self.fig = plt.figure()
        self.ax = plt.axes(projection='3d')
        self.curr_centroid = self.getCentroid()
        self.curr_orientation = (0, 0, 0)
        self.T = Transform(centroid=self.curr_centroid)
        self.orig_centroid = self.curr_centroid
        self.orig_orientation = self.curr_orientation
        self.align(45, 45, 'z')

    # Plotting Methods
    def plotSTL(self):
        ''' Plots the STL object on a standard 3D platform'''
        self.setToJustBuildPlate()
        self.plotFaces()
        self.fitToBuildSpace()
        plt.show()

    def plotFaces(self):    
        ''' Plots each face in the STL''' 
        for face in self.stl.faces:
            self.plotFace(face)

    def plotFace(self, face: Face, color=[30/255, 144/255, 255/255, 1]):
        ''' Plots the inputted face as a polygon. The default color is Dodger 
        Blue.'''
        x = face.getXCoordinates()
        y = face.getYCoordinates()
        z = face.getZCoordinates()

        vertices = [list(zip(x, y, z))]
        polygon = Poly3DCollection(vertices)
        #TODO: Change so facecolor is a function of normal and z
        polygon.set_facecolor(color) #Set face to blue
        polygon.set_edgecolor((0, 0, 0)) #Set edge to black
        self.ax.add_collection3d(polygon)

    # Formatting Methods
    def clearPlot(self):
        ''' Resets the axis (clearing any current figures)'''
        self.ax.clear()

    def setToJustBuildPlate(self):
        ''' Removes all plotting marks and plots the build plate'''
        self.ax.grid(False)
        self.setAxisLines(on=False)
        self.setBackground()
        self.plotBuildPlate()
        self.turnOffAxisTicks()

    def setAxisLines(self, on: bool):
        ''' Either shows or covers the axis lines'''
        if on: color = (0.0, 0.0, 0.0, 1.0)
        else: color = (1.0, 1.0, 1.0, 0.0)
        self.ax.w_xaxis.line.set_color(color)
        self.ax.w_yaxis.line.set_color(color)
        self.ax.w_zaxis.line.set_color(color)

    def setBackground(self, xplane=(1.0, 1.0, 1.0, 0.0), \
        yplane=(1.0, 1.0, 1.0, 0.0), zplane=(1.0, 1.0, 1.0, 0.0)):
        ''' Sets the color of the panes in the 3D plot. The default is
        to hide all planes. The input type for each is (red, green, blue, 
        alpha).'''
        self.ax.xaxis.set_pane_color(xplane)
        self.ax.yaxis.set_pane_color(yplane)
        self.ax.zaxis.set_pane_color(zplane)

    def plotBuildPlate(self, width=203.2, depth=152.4):
        ''' Plots the a flat plane simulating the build plate centered at 
        the origin.'''
        vertices = [[(-width/2, -depth/2, 0), (width/2, -depth/2, 0), 
                    (width/2, depth/2, 0), (-width/2, depth/2, 0)]]
        polygon = Poly3DCollection(vertices)
        color = (0.4, 0.4, 0.4, 0.2)
        polygon.set_facecolor(color) #Set face to grey
        polygon.set_edgecolor(color) #Set edge to grey
        # polygon.set_zsort({})
        self.ax.add_collection3d(polygon, zs=-10)

    def turnOffAxisTicks(self):
        ''' Removes the tick marks from the axes.'''
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_zticks([])

    def defineLabels(self, title='STL Plot', xlabel='X Axis', \
        ylabel='Y Axis', zlabel='Z Axis'):
        ''' Sets labels for the title and axes'''
        self.ax.set_title(title)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.set_zlabel(zlabel)

    def setLimits(self, xlimit=(-10, 10), ylimit=(-10, 10), zlimit=(-10, 10)):
        ''' Sets limits for the axes. The input is for each axis is (lower 
        bound, upper bound)'''
        self.ax.set(xlim=xlimit, ylim=ylimit, zlim=zlimit)

    # View Methods
    def fitAxes(self):
        ''' Fits each axis to the maximum size of the STL. The part is 
        guaranteed to show in the plot, though objects that are larger in a
        single dimension will also have lots of blank space. The axes are
        squared.'''
        limits = self.findMaxAndMinLimits()
        max_val = max(limits)
        min_val = min(limits)
        clrnc = max_val * 0.05 if abs(max_val) > abs(min_val) else min_val * 0.05
        max_lim = max_val + clrnc
        min_lim = min_val - clrnc
        self.setLimits(xlimit= (min_lim, max_lim), \
                       ylimit= (min_lim, max_lim), \
                       zlimit= (0, max_lim - min_lim))

    def fitToBuildSpace(self, dim=203.2):
        ''' Fits the axis to the build space (but squared).'''
        xylimits = (-dim/2, dim/2)
        self.setLimits(xlimit= xylimits, \
                       ylimit= xylimits, \
                       zlimit= (0, dim))

    def align(self, elev, azim, vertical_axis='z'):
        ''' Aligns the axes to the inputted elevation and azimuth. Also
        orientes the axes so that the vertical axis is vertical to the viewer.'''
        self.ax.view_init(elev, azim, vertical_axis)

    def alignXY(self):
        ''' Aligns the screen so that the XY plane is parallel to the screen'''
        self.align(0, 0, 'y')

    def alignYZ(self):
        ''' Aligns the screen so that the YZ plane is parallel to the screen'''
        self.align(0, 0, 'z')

    # Transformation Methods
    def getCentroid(self):
        x = list()
        y = list()
        z = list()
        for face in self.stl.faces:
            x.append(face.getXCoordinates())
            y.append(face.getYCoordinates())
            z.append(face.getZCoordinates())
        return [np.mean(x), np.mean(y), np.mean(z)]

    def rotate(self, theta: float=0., phi: float=0., psi: float=0.):
        ''' Rotates the STL along a coordinate system centerd at the centroid of the object

        Notes
        ---
        The order of rotation is around the x axis, then y axis, then z axis. Function 
        calls with multiple rotations must follow this order. To rotate in a different 
        order, call the function multiple times with a single rotation per function call.'''
        self.T.rotateInPlace(theta=theta, phi=phi, psi=psi)

    def translate(self, delx: float=0, dely: float=0, delz: float=0):
        ''' Translates the STL along the three axes.'''
        self.T.translate(delx=delx, dely=dely, delz=delz)

    def orthographic(self, view: str):
        ''' Orients the part to an orthographic view (where front is defined as the
        orientation of the part when it was initially loaded). 
        
        Inputs
        ---
        view : str ("front", "back", "right", "left", "top", "bottom")
            The view to rotate to. If the input is not one of the specified values
            the function prints a warning message to the screen but otherwise makes
            no action.
        '''
        self.T.rotateToFront()
        label = view.lower()
        if label == 'front': return
        elif label == 'back': self.rotate(psi=np.pi)
        elif label == 'right': self.rotate(psi=-np.pi/2)
        elif label == 'left': self.rotate(psi=np.pi/2)
        elif label == 'top': self.rotate(phi=np.pi/2)
        elif label == 'bottom': self.rotate(phi=-np.pi/2)
        else: print("Incorrect parameter ({}) passed to function \"orthographic\"".format(view))

    def moveToFloor(self):
        ''' Lowers the part until the lowest part of the object sits on the z plane'''
        limits = self.findMaxAndMinLimits()
        zmin = limits[4]
        self.translate(delz=-zmin)

    def moveToCenter(self):
        ''' Moves the STL to the vertical center of the screen (along y-axis only)'''
        # ylim = plt.gca().get_ylim()
        # y_center = (ylim[1] - ylim[0]) / 2 + ylim[0]
        dely = 0 - self.curr_centroid[1]
        self.translate(dely=dely)

    def updateSTL(self):
        ''' Applies the transformations encoded in self.T to the STL vertices, then 
        resets self.T for further transformations.'''
        for face in self.stl.faces:
            A = np.array(face.getMatrix())
            npA = self.T.transform(A)
            face.loadFromMatrix(npA.tolist())
        self.curr_centroid = self.T.curr_centroid
        self.curr_orientation = self.T.curr_orientation
        self.T = Transform(orientation=self.curr_orientation, centroid=self.curr_centroid)

    # Slicing Methods
    def sliceAndPlot(self, layer_height=0.2):
        self.slice(layer_height)
        self.plotSlicedModel()

    def slice(self, layer_height):
        self.slicer = Slicer(self.stl, layer_height)
        self.slicer.sliceSTL()

    def plotSlicedModel(self):
        self.clearPlot()
        for i in range(len(self.slicer.slices)):
            self.plotLayer(i)
        self.setToJustBuildPlate()
        self.fitToBuildSpace()

    def plotLayer(self, layer_index, color=(0, 0.6, .13, 0.5)):
        if layer_index < 0 or layer_index >= len(self.slicer.slices):
            return
        slice = self.slicer.slices[layer_index]
        for hull in slice.hulls:
            xline, yline, zline = hull.getXYZCoordinates()
            vertices = [list(zip(xline, yline, zline))]
            polygon = Poly3DCollection(vertices)
            polygon.set_facecolor(color) 
            polygon.set_edgecolor(color)
            self.ax.add_collection3d(polygon)

    def highlightLayer(self, layer_index, color=(1, 0, 0, 0.8)):
        self.clearPlot()
        self.setToJustBuildPlate()
        self.fitToBuildSpace()
        for i in range(layer_index):
            self.plotLayer(i)
        self.plotLayer(layer_index, color)
    
    # Service Methods
    def findMaxAndMinLimits(self):
        ''' Finds the highest and lowest vertex along each axis. The output is
        [xmin, xmax, ymin, ymax, zmin, zmax]'''
        limits = [0, 0, 0, 0, 0, 0]
        vertices = self.stl.getAllVertices()
        for vertex in vertices:
            for i in range(3):
                if vertex[i] < limits[i*2]: limits[i*2] = vertex[i]
                if vertex[i] > limits[i*2+1]: limits[i*2+1] = vertex[i]
        return limits