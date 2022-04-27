# %%
from ReadSTL import STL
from PlotSTL import PlotSTL

    
# %%
stl = STL("../../Sample STL Files/Eiffel Tower 760.stl")
plotter = PlotSTL(stl)
plotter.moveToCenter()
plotter.updateSTL()
plotter.sliceAndPlot(10)
plotter.highlightLayer(13)

# %%
