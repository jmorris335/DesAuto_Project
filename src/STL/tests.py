# %%
from ReadSTL import STL
from PlotSTL import PlotSTL
    
# %%
# stl = STL("../../Sample STL Files/Eiffel Tower 760.stl")
# stl = STL("../../Sample STL Files/Simple 8.stl")
stl = STL("../../Sample STL Files/Cube 432.stl")
plotter = PlotSTL(stl)
plotter.moveToCenter()
# plotter.rotate(phi=-3.14159/2)
plotter.moveToFloor()
plotter.updateSTL()
plotter.buildExtrusion(1, .5, .2)
plotter.plotExtrudedUptoLayer(100)
plotter.align(90, 270, 'z')
# plotter.setLimits((-33, -15), (33, 15)) 

# %%