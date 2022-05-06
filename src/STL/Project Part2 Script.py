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
from STL.Extrusion import Extrusion, Path, calcInfillData

"""
This script is made to complete the requirements of the Clemson Design Automation Project Part 2 (Spring 2022)
Below are the user inputs that are set to the defaults"""

#user inputs
stl_file = 'Simple 8.stl'
cur_path = os.path.dirname(__file__)
stl_filepath = os.path.join(cur_path, '..', 'Sample STL Files', stl_file)

slicing_interval = .25 #mm
num_print_layers = 6

#1. load the STL
stl = STL(file = stl_filepath)

#2. Scale, orient, and clip the model
mm2in = 1/25.4 #conversion factor to inches from millimeters
build_plate_dimm = (8, 8, 6) #dimmensions of the build plate

T = Transform()
T.scale(x = mm2in, y = mm2in, z = mm2in)
T.translateToOrigin()
T.translate(delx = build_plate_dimm[0]/2, dely = build_plate_dimm[1]/2, delz = build_plate_dimm[2]/2)
buildSTL = PlotSTL(stl)
buildSTL.T = T
buildSTL.updateSTL()

buildSTL.stl = clipping(buildSTL.stl, build_plate_dimm)

#3. display the model
"""Currently there is no GUI so I will use MatPlotLib to plot the resulting model"""
buildSTL.plotSTL()

#4. slice the model according to slicing interval (user set)
slices = Slicer(buildSTL.stl, slicing_interval, 0, build_plate_dimm[2])

#5. create a tab-deliminated .txt file of 6 slices equally spaced throught the part
txt_file_name = stl_file[0:-4] + '_slices.txt'
txt_filepath = os.path.join(txt_file_name)
f = open(txt_filepath, 'w')

slice_dist = len(slices) // num_print_layers
print_list = []
for i in range(num_print_layers):
    print_list.append(slices[i * slice_dist])
print_list.append(slices[-1])

all_coords = [[],[],[]]
for slice in print_list:
    all_coords[0].slice.getXYZCoordinates()[0]
    all_coords[1].slice.getXYZCoordinates()[1]
    all_coords[2].slice.getXYZCoordinates()[2]
    for i in range(len(all_coords[0])):
        if i < (len(all_coords[0])-1):
            f.write("t" + i + "\t" + all_coords[0][i] + "\t" + all_coords[1][i] + "\t" + all_coords[2][i] + "\t" + "1\n")
        else:
            f.write("t" + i + "\t" + all_coords[0][i] + "\t" + all_coords[1][i] + "\t" + all_coords[2][i] + "\t" + "0\n")

f.close()

#6. Infill layers
infill = Extrusion(buildSTL.stl)

