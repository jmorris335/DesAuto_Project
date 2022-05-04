# %%
from ReadSTL import STL
from PlotSTL import PlotSTL
from Transform import Transform
    
# %%
stl = STL("../../Sample STL Files/Eiffel Tower 760.stl")
# stl = STL("../../Sample STL Files/Simple 8.stl")
# stl = STL("../../Sample STL Files/Cube 432.stl")
plotter = PlotSTL(stl)
# plotter.moveToCenter()
# plotter.updateSTL()
# plotter.plotSTL()
plotter.buildExtrusion(.25, .25, .2)
plotter.plotExtrudedUptoLayer(10)
plotter.align(90, 270, 'z')
plotter.setLimits((18, 30), (-30, -18)) 
# plotter.plotExtrusion(wall_thickness=1, layer_height=15, infill_density=0.001)


# %%
pi = 3.14159256
X = Transform()
X.translate(dely=5)
X.updateT()
normal = [0, -.5, -.5]
print(X.transformNorm(normal))


# %%