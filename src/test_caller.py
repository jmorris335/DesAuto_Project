# %%
from os import path

from STL.ReadSTL import STL
from STL.PlotSTL import PlotSTL
from STL.Clipping import clipping

stl_file = 'Simple 8.stl'
cur_path = path.dirname(__file__)
stl_filepath = path.join(cur_path, '..', 'Sample STL Files', stl_file)

# Test 1: Load and Create Object
testObj = STL(stl_filepath)
print(testObj.toString())

# # Test 2: Plot and rotate STL
# testPlt = PlotSTL(testObj)
# testPlt.orthographic("left") #Rotate to left view of STL
# testPlt.rotate(psi=np.pi/4) #Rotate pi/4 radians around the vertical axis
# testPlt.moveToFloor() #Lower the STL to the floor
# testPlt.moveToCenter() #Move the STL to the center of the build plate
# testPlt.updateSTL() #Load all transformations
# testPlt.plotSTL() #Plot the STL to the screen

# # Test 3: Copy object into clippable object
# emptyCopy = testObj.emptyCopy()
# print(emptyCopy.toString())
# emptyCopy.faces = testObj.faces
# print(emptyCopy.toString())

# Test 4: Clipping
# clipped = clipping(testObj, (5, 8, 10))
# plot_c = PlotSTL(clipped)
# plot_c.plotSTL()
# plot_c.align(90, 270, 'z')
# plot_c.setLimits((-1, 6), (-1, 9)) 

# Test 5: Plot updating
plot = PlotSTL(testObj)
plot.orthographic('back')
plot.updateSTL()
plot.orthographic('top')
