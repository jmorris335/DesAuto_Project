import numpy as np

import sys
sys.path.insert(0, '..')

from STL.ReadSTL import STL
from STL.PlotSTL import PlotSTL

testObj = STL("Sample STL Files\House4 106.stl")
print(testObj.toString())

testPlt = PlotSTL(testObj)
testPlt.orthographic("left") #Rotate to left view of STL
testPlt.rotate(psi=np.pi/4) #Rotate pi/4 radians around the vertical axis
testPlt.moveToFloor() #Lower the STL to the floor
testPlt.moveToCenter() #Move the STL to the center of the build plate
testPlt.updateSTL() #Load all transformations
testPlt.plotSTL() #Plot the STL to the screen