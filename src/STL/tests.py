# %%
import matplotlib.pyplot as plt
# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

from ReadSTL import STL
from PlotSTL import PlotSTL
from SliceSTL import Slicer

class TestSliceSTL:
    def __init__(self, slicer: Slicer):
        self.slicer = slicer
        self.fig = plt.figure()
        self.ax = plt.axes(projection='3d')

    def plot(self):
        for slice in self.slicer.slices:
            for hull in slice.hulls:
                xline, yline, zline = hull.getXYZCoordinates()
                self.ax.plot3D(xline, yline, zline)

    def align(self, elev, azim, vertical_axis='z'):
        ''' Aligns the axes to the inputted elevation and azimuth. Also
        orientes the axes so that the vertical axis is vertical to the viewer.'''
        self.ax.view_init(elev, azim, vertical_axis)

    
# %%
stl = STL("../../Sample STL Files/Eiffel Tower 760.stl")
slicer = Slicer(stl, .1)
slicer.sliceSTL()
testSlicer = TestSliceSTL(slicer)
testSlicer.align(10, 45, 'z')
testSlicer.plot()
# plotter = PlotSTL(stl)
# plotter.plotSTL()

# %%