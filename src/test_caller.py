# %%
import numpy as np
import sys
sys.path.insert(0, '..') # To access the Sample STL Files directory

from STL.ReadSTL import STL
from STL.PlotSTL import PlotSTL

# Test 1: Load and Create Object
testObj = STL("..\..\Sample STL Files\House4 106.stl")
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
# %%
clippedSTL = testObj.clipping((2, 3, 2))
plottedClipped = PlotSTL(clippedSTL)
plottedClipped.plotSTL()