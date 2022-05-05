import numpy as np
import os
from copy import deepcopy
from math import floor, ceil

from STL.ReadSTL import STL, STL_Facet as facet
from STL.Clipping import clipping
from Transform import Transform
from src.STL.PlotSTL import PlotSTL
import STL.Methods as mthd
from STL.SliceSTL import Edge, Hull, Slicer

"""
This script is made to complete the requirements of the Clemson Design Automation Project Part 2 (Spring 2022)
Below are the user inputs that are set to the defaults"""

#user inputs
stl_file = 'Simple 8.stl'
cur_path = os.path.dirname(__file__)
stl_filepath = os.path.join(cur_path, '..', 'Sample STL Files', stl_file)

slicing_interval = .2 #mm

#1. load the STL
stl = STL(file = stl_filepath)

#2. Scale, orient, and clip the model
mm2in = 1/25.4 #conversion factor to inches from millimeters
build_plate_dimm = (8, 8, 6) #dimmensions of the build plate

T = Transform()
T.scale(x = mm2in, y = mm2in, x = mm2in)
T.translateToOrigin()
T.translate(delx = build_plate_dimm[0]/2, dely = build_plate_dimm[1]/2, delz = build_plate_dimm[2]/2)
buildSTL = PlotSTL(stl)
buildSTL.T = T
buildSTL.updateSTL()

buildSTL.stl = clipping(buildSTL.stl)

#3. display the model
"""Currently there is no GUI so I will use MatPlotLib to plot the resulting model"""
buildSTL.plotSTL()

#4. slice the model according to slicing interval (user set)
slices = Slicer(buildSTL.stl, slicing_interval, 0, build_plate_dimm[2])
