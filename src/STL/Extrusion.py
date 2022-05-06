from math import floor

from src.STL.ReadSTL import STL
from src.STL.SliceSTL import Slicer, Hull, Slice
from src.STL.Offset import getOffsetSTL
import src.STL.Methods as mthd

'''
Status: This class creates a grid infill properly, and makes paths for the outer
hulls correctly. It requires the offset module functionality to be finished before 
it can create the border walls effectively. At that point it will use the offset 
functionality to create the solid-infill border walls. -JM, 5 May 2022
'''

class Path:
    def __init__(self, points):
        ''' An ordered set of coordiantes describing the path of an extruder head
        to lay down filament. '''
        self.points = points

    def calcPathLength(self):
        ''' Returns the full length of the path, in the units of the original
        coordinates.'''
        distance = 0
        for i in range(len(self.points)-1):
            distance += mthd.euclidianDistance(self.points[i], self.points[i+1])
        return distance

    def getXYZ(self):
        ''' Returns a tuple of 3 lists of x, y, and z coordinates respectively'''
        x = list()
        y = list()
        z = list()
        for pnt in self.points:
            x.append(pnt[0])
            y.append(pnt[1])
            z.append(pnt[2])
        return x, y, z

    @staticmethod
    def toLine(point, extrude: True):
        return 'X' + str(point[0]) + '\tY' + str(point[1]) + '\tZ' + str(point[2])

    def toString(self):
        ''' Returns an output of the path in two lines.'''
        line1 = self.toLine(self.points[0], True)
        line2 = self.toLine(self.points[1], False)
        return [line1, line2]

class Extrusion:
    def __init__(self, stl: STL, wall_thickness=1.5, layer_height=0.25, infill_density=0.2):
        ''' An object that takes an STL and calculates the necessary paths an
        FFF extruder must traverse to recreate the object. Note that all units are in mm.
        
        Inputs
        ---
        stl : STL
            The STL object (from ReadSTL module)
        wall_thickness, default: 1.5
            The thickness of the wall. In theory should be a multiple of the 
            layer height in order to be exact.
        layer_height, default: 0.25
            The thickness of each layer. This is treated as equivalent to the width of
            each extrusion path.
        infill_density : float between 0 and 1, default: 0.2
            The density of the infill. 0.15 through 0.20 is typical. 1 correlates to a
            solid infill, while 0 removes infill. Infill percentages are based on a 1mm
            by 1mm square area.
        '''
        self.stl = stl
        self.innerSTL = stl
        self.wall_thickness = wall_thickness
        self.layer_height = layer_height
        self.density = abs(infill_density) if abs(infill_density) <= 1 else 1
        self.numWalls = int(wall_thickness / layer_height)
        self.numWalls = 1 #FIXME: This prevents offsetting until that functionality is established
        self.printing_speed = 25.4 #mm/s
        self.length_of_print = 0
        self.time_to_print = 0
        self.setupSlices()
        self.findInfillCoord()
        self.makeBorderWalls()
        self.makeInfill()

    def setupSlices(self):
        ''' Calculates the number of slices, and creates several class members.'''
        temp = Slicer(self.stl, self.layer_height)
        self.numSlices = temp.numSlices
        self.slices = [[] for i in range(self.numSlices)]
        self.z_index = [i * self.layer_height for i in range(self.numSlices)]
        if temp.additionalSliceOnTop: self.z_index[-1] = temp.max_z

    def findInfillCoord(self):
        ''' Finds the coordinates of the beginning of each infill path. The infill path
        follows a grid (horizontal and vertical). The coordinate pairs go from left to 
        right, bottom to top, so that coordinates will start in Quadrant III.'''
        self.limits = Slicer.findMaxAndMinLimits(self.stl)
        self.horz_coord = list()
        self.vert_coord = list()
        x = self.limits[0]
        y = self.limits[2]
        spacing = calcInfillData(self.layer_height, self.density)
        while y <= self.limits[3]:
            self.horz_coord.append((self.limits[0], y))
            y += spacing
        while x <= self.limits[1]:
            self.vert_coord.append((x, self.limits[2]))
            x += spacing

    def getSliceIndex(self, z, tol=1e-5):
        ''' Returns the index of slice that contains the z datum. Returns None if 
        the inputted z is not contained in any slice.'''
        if z < self.layer_height - tol: return 0
        if z > self.z_index[-1] + tol: return None
        for i in range(len(self.z_index)):
            if abs(self.z_index[i] - z) < tol: return i
        return None

    def addSliceHulls(self, slice: Slice):
        ''' Takes the hulls in a slice and adds them to the extrude paths. Each hull
        is treated as a boundary wall.'''
        for i in range(len(slice.hulls)):
            self.addPath(Path(slice.hulls[i].pnts))
    
    def addPath(self, path: Path):
        ''' Adds a path to the Extrusion object.'''
        index = self.getSliceIndex(path.points[0][2])
        if index != None:
            self.slices[index].append(path)
            length = path.calcPathLength()
            self.length_of_print += length
            self.time_to_print += length / self.printing_speed

    def printMass(self, density=0.00125, filament_circumference=1.75):
        ''' Returns the estimated mass of the print in grams. Units are g/mm^3 and mm.
        The default values are for PLA filament (.00125 g/mm^3). ABS is .00104 g/mm^3.'''
        return self.length_of_print * filament_circumference * 3.1415926 * density

    # Make Paths
    def makeBorderWalls(self):
        ''' Finds the paths for each of the border walls and adds it to the Extrusion
        object. Also sets the innerSTL to the be the innermost border wall for use in
        infill calculation.'''
        min_z = None
        max_z = None
        for i in range(self.numWalls):
            temp = Slicer(self.innerSTL, self.layer_height, min_z, max_z)
            min_z = temp.min_z
            max_z = temp.max_z
            temp.sliceSTL()
            for slice in temp.slices:
                self.addSliceHulls(slice)
            if i != self.numWalls-1: 
                self.innerSTL = getOffsetSTL(temp.stl, -self.layer_height/2)
            self.slicedSTL = temp

    def makeInfill(self):
        ''' Caller function to make the infill paths for each slice in the object.'''
        # Delete below if uncommenting self.makeBorderWalls()
        # temp = Slicer(self.innerSTL, self.layer_height)
        # temp.sliceSTL()
        # self.slicedSTL = temp
        # Delete above
        for slice in self.slicedSTL.slices:
            for hull in slice.hulls:
                paths = self.fillHull(hull)
                for path in paths: self.addPath(path)

    def fillHull(self, hull: Hull):
        ''' Returns a set of infill paths traversing the hull.'''
        paths = list()
        for y_c in self.horz_coord:
            paths.extend(self.getPaths(y_c[1], hull, is_horizontal=True))
        for x_c in self.vert_coord:
            paths.extend(self.getPaths(x_c[0], hull, is_horizontal=False))
        return paths
        
    def getPaths(self, l_c, hull: Hull, is_horizontal):
        ''' Gets the set of horizontal paths within the hull.'''
        paths = list()
        iscts = list()
        normals = list()
        for i in range(len(hull.pnts)-1):
            isct = self.findLineSegIntersection(hull.pnts[i], hull.pnts[i+1], l_c, is_horizontal)
            if isct != None:
                iscts.append(isct)
                normals.append(hull.normals[i])
        if len(iscts) > 1:
            paths.extend(self.makePaths(iscts, normals, is_horizontal))
        return paths

    def makePaths(self, intersection_points, normals, is_horizontal: bool):
        ''' Returns a set of horizontal paths running between the intersection_points.'''
        isct = mthd.orderPoints(intersection_points)
        normals = mthd.sortByOrderedSet(normals, isct, intersection_points)
        paths = list()
        start = None
        for i in range(len(isct)):
            dir = mthd.NormalSign(normals[i], is_horizontal)
            if dir == 0: continue
            elif dir == -1: start = isct[i]
            elif dir == 1: 
                if start != None:
                    paths.append(Path([start, isct[i]]))
                start = None
        return paths

    def findLineSegIntersection(self, pnt1, pnt2, line_c, is_horizontal=True, tol=1e-5):
        ''' Returns the intersection point (as a tuple) of the line segment defined by
        pnt1 and pnt2 with the vertical or horizontal line located at the coordinate
        line_c, with orientation given by is_horizontal. If the lines are colinear, 
        returns None.'''
        if len(pnt1) > 3: z = 0
        else: z = pnt1[2]
        delx = pnt2[0] - pnt1[0]
        if abs(delx) <= tol:
            if is_horizontal and mthd.horizontalIntersectsLineSeg(line_c, [pnt1, pnt2]): 
                return (pnt1[0], line_c, z)
            else: return None
        m = (pnt2[1] - pnt1[1]) / (pnt2[0] - pnt1[0])
        if is_horizontal:
            if not mthd.horizontalIntersectsLineSeg(line_c, [pnt1, pnt2]): return None
            return ((line_c - pnt1[1]) / m + pnt1[0], line_c, z)
        else:
            if not mthd.verticalIntersectsLineSeg(line_c, [pnt1, pnt2]): return None
            return (line_c, m * (line_c - pnt1[0]) + pnt1[1], z)

def calcInfillData(layer_height, density, side=1000):
    ''' Calculates the spacing and number of lines for the infill, based on a unit
    square of length side (higher values of side are more precise).'''
    num_lines = floor(side * (1 - (1-density)**(1/2)) / layer_height)
    spacing = (side - layer_height * num_lines) / (num_lines + 1)
    spacing = round(spacing, 3)
    return spacing