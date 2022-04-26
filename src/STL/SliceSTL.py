# %%
from copy import deepcopy
from math import floor, ceil
import numpy as np
from ReadSTL import STL, STL_Facet as Facet

class Edge:
    def __init__(self, pnt1, pnt2, normal):
        ''' An edge is a line segment terminated by two points with a single
        normal vector describing which direction is out.'''
        self.pnt1 = pnt1
        self.pnt2 = pnt2
        self.normal = normal

class Slice:
    def __init__(self, points, normals):      
        ''' A collection of edges that define a slice.'''
        self.pnts = points
        self.normals = normals
        self.z_datum = points[0][0]

    #FIXME: Add methods for accessing a certain edge, getting all coordinates, etc.

class Slicer:
    def __init__(self, stl: STL, layer_height):
        ''' Takes an stl object and returns a list of Slice objects, where each
        slice represents a layer of the STL object, sliced in the z-direction.

        Inputs
        ---
        stl : STL
            The scaled stl object, defined in ReadSTL.py
        layer_height : 
            A float or int representing the height of each layer in the units
            of the stl coordinates.
        
        Process
        ---
        1. Pass the object. Determine number of slices
        2. For each slice:
            a. Find which faces intersect the plane of the slice
            b. Determine the intersection coordinates
            c. Form line segments out of each face intersection
            d. Connect line segments with similar endpoint coordinates
        6. Form the slice and repeat until the max z-coordinate is reached
        '''
        self.stl = stl
        self.del_z = layer_height
        limits = self.findMaxAndMinLimits()
        self.max_z = limits[5]
        self.min_z = limits[4]
        self.slices = list()
        self.numSlices = self.findNumOfSlices()
        self.findFacetsAtEachSlice()

    # Setup Functions
    def findNumOfSlices(self):
        ''' Returns the maximum number of slices in the object, including the
        slice at the bottom (z_min) and top (z_max).'''
        numSlices = ceil((self.max_z - self.min_z) / self.del_z)
        if self.addAdditionalSliceOnTop(): numSlices += 1 #Also slice at the top of the part
        return numSlices

    def addAdditionalSliceOnTop(self):
        ''' Returns true if the program should create another slice at the max
        z height (z_max), or if the top layer was already included in the slices 
        at the intervals of the layer height.'''
        self.additionalSliceOnTop = self.max_z % self.del_z != 0
        return self.additionalSliceOnTop

    def findFacetsAtEachSlice(self):
        ''' Creates an list where each entry contains the faces covered by the 
        slice at the corresponding index'''
        self.facet_groups = [list() for i in range(self.numSlices+1)]
        for face in self.stl.faces:
            indices = self.findSlicesCoveredByFace(face)
            for index in indices: 
                self.facet_groups[index].append(face)

    def findSlicesCoveredByFace(self, facet: Facet):
        ''' Returns a the range of indices to which slices contain the given facet. The list
        corresponds with the faces in stl.faces. Note that the indices start at 0
        for the bottom slice (at z_min), and end with numSlices - 1 for the top slice 
        (at z_max).'''
        zcoord = facet.getZCoordinates()
        starting_index = floor((min(zcoord) - self.min_z) / self.del_z)
        ending_index = ceil((max(zcoord) - self.min_z) / self.del_z)
        if max(zcoord) == self.max_z and self.additionalSliceOnTop: 
            ending_index += 1
        return range(starting_index, ending_index)

    # def sliceSTL(self):
    #     slices_points = self.getCoordinatesOfSlices()
    #     self.formEdgesFromCoordinates(slices_points)

    # Slicing Functions
    def sliceSTL(self):
        all_unsorted_edges = self.getEdgesForAllSlices()
        for unsorted_edges in all_unsorted_edges:
            sorted_points, sorted_normals = self.stitchEdges(unsorted_edges)
            temp = Slice(sorted_points, sorted_normals, layer_height)
            self.slices.append(temp)

    def getEdgesForAllSlices(self):
        ''' Returns a list of lists, where each entry corresponds to a list of all the edges 
        for each slice.'''
        slices_edges = list()
        for layer_index in range(self.numSlices):
            z_datum = self.min_z + (layer_index * self.del_z)
            slices_edges.append(self.getSliceEdges(layer_index, z_datum))
        slices_edges.append(self.getSliceEdges(self.numSlices-1, self.max_z))
        return slices_edges

    # def getCoordinatesOfSlices(self): #References wrong function
    #     ''' Returns a list of lists, where each entry corresponds to a list of all the edge
    #     points for each slice.'''
    #     slices_points = list()
    #     for layer_index in range(self.numSlices):
    #         z_datum = self.min_z + (layer_index * self.del_z)
    #         slices_points.append(self.getSlicePoints(layer_index, z_datum))
    #     slices_points.append(self.getSlicePoints(self.numSlices-1, self.max_z))
    #     return slices_points

    # def getSlicePoints(self, layer_index, z_datum): #Not Working
    #     ''' Returns the coordinates for the intersections of the edges of each face that
    #     crosses the z_datum plane, as well as the normal of the generating face.'''
    #     out = list()
    #     facets_in_slice = self.facet_groups[layer_index]
    #     for face in facets_in_slice:
    #         pnts = face.vertices
    #         for i in range(len(pnts)-1):
    #             if self.lineIntersectsDatum(pnts[i], pnts[i+1], z_datum):
    #                 points = self.interpolateZ(pnts[i], pnts[i+1], z_datum)
    #                 for point in points:
    #                     out.append((point, face.normal))
    #     return out

    def getSliceEdges(self, layer_index, z_datum):
        ''' Returns a list of edges contained in the slice referenced by the 
        layer_index, which corresponds to the plane located at the z_datum.'''
        out = list()
        facets_in_slice = self.facet_groups[layer_index]
        for face in facets_in_slice:
            edges = self.getEdgesFromFace(face, z_datum)
            if edges != None: out.append(edges)
        return out

    def getEdgesFromFace(self, face: Facet, z_datum):
        ''' Returns a list of edges derived from the intersection of the face with
        the z_datum plane. Returns none if there are no intersection edges (or if 
        the face intersects only at a single point).'''
        edges = list()
        coord = self.getIntersectionPointsFromFace(face, z_datum)
        if len(coord) <= 1: return None
        for i in range(len(coord)-1):
            edges.append(Edge(coord[i], coord[i+1], face.normal))
        if len(coord) > 2:
            edges.append(Edge(coord[len(coord)-1], coord[0], face.normal))
        return edges

    def getIntersectionPointsFromFace(self, face: Facet, z_datum):
        ''' Returns a list of all the intersection points between a face and the
        z_datum'''
        pnts = face.vertices
        intersection_pnts = list()
        indices = range(len(pnts))
        indices.append(0)
        for i in indices:
            temp = self.interpolateZ(pnts[i], pnts[i+1], z_datum)
            if temp != None: intersection_pnts.append(temp)
        return intersection_pnts
        
    def stitchEdges(self, edges):
        ''' Organizes all edges into a hull (either convex or concave). Fails if there is
        self intersecting geometry. Returns a list of points and a list of normals, where
        the normal[i] correspondes to the normal of the line segment between points[i] and
        points[i+1]'''
        next_edge = edges[0]
        points_out = [next_edge.pnt2]
        normals_out = list()
        for i in range(len(edges)):
            next_pt, next_edge = self.findJoiningPoint(points_out[i], next_edge, edges)
            points_out.append(next_pt)
            normals_out.append(next_edge.normal)
        return points_out, normals_out

    def findJoiningPoint(self, pnt, curr_edge: Edge, edges):
        ''' Parses through edges looking for an edge that has a similar coordinate as
        "pnt", but is not the exact same edge. Returns the associated point in the new
        edge as well as the edge.'''
        for edge in edges:
            if edge == curr_edge: continue
            if self.checkSimilarTuples(pnt, edge.pnt1):
                return edge.pnt2, edge
            elif self.checkSimilarTuples(pnt, edge.pnt2):
                return edge.pnt1, edge
        
    # def formEdgesFromCoordinates(self, slices_points):
    #     ''' Parses through a list of points in a slice and compiles each point into an
    #     edge, then adds those edges to a slice, which is appended to a member variable.'''
    #     self.slices = list()
    #     for slice_points in slices_points:
    #         slice_edges = list()
    #         for i in range(len(slice_points)-1):
    #             pnt_nrm1 = slice_points[i]
    #             pnt_nrm2 = slice_points[i+1]
    #             edge = self.makeEdge(pnt_nrm1, pnt_nrm2)
    #             if edge != None: slice_edges.append(edge)
    #         if len(slice_edges) > 0:
    #             self.slices.append(Slice(slice_edges, self.del_z))

    # def makeEdge(self, point_normal1, point_normal2):
    #     ''' Creates an Edge from two tuples constructed as (point, normal), where both
    #     point and normal are (1x3) tuples. If the two points are too close to each other, 
    #     the function returns None'''
    #     point1 = point_normal1[0]
    #     point2 = point_normal2[0]
    #     if self.checkSimilarTuples(point1, point2): return None
    #     else: return Edge(point1, point2, point_normal1[1])

    def lineIntersectsDatum(self, pnt1, pnt2, z_datum):
        ''' Returns true if the line segment connecting pnt1 and pnt2 intersects the 
        plane at z_datum and parallel to the XY plane'''
        if pnt1[2] >= z_datum:
            if pnt2[2] <= z_datum: return True
            else: return False
        if pnt2[2] >= z_datum: return True
        return False
                
    # Service Functions
    @staticmethod
    def interpolateZ(pnt1, pnt2, z_datum):
        ''' Returns the point on the line corresponding to the z_datum. If the line is 
        contained on the plane parallel to the XY plane and intersecting the z_datum, 
        then the function returns the first point. If the line does not intersect the 
        plane then the function returns None.'''
        m = list()
        for i in range(len(pnt1)): m.append(pnt2[i] - pnt1[i])
        if m[2] == 0: 
            if pnt1[2] == z_datum:
                return pnt1
            else: return None
        else: 
            t = (z_datum - pnt1[2]) / m[2]
            x_new = pnt1[0] + t * m[0] 
            y_new = pnt1[1] + t * m[1]
        return (x_new, y_new, z_datum)

    @staticmethod
    def isOutOfBounds(coords: list, start, end):
        ''' Checks if any of the inputted coordinates are outside the boundary
        defined by start, end.'''
        for coord in coords:
            if (coord > start) & (coord < end): return False
        return True

    @staticmethod
    def checkSimilarTuples(tuple1, tuple2, tol=0.01):
        ''' Checks if the coordinates of the two tuples are within a certain tolerance
        of each other.'''
        if tuple1 == tuple2: return True
        if len(tuple1) != len(tuple2): return False
        err = 0
        for i in range(len(tuple1)):
            err += abs(tuple1[i] - tuple2[i])
        return err <= tol

    def findMaxAndMinLimits(self):
        ''' Finds the highest and lowest vertex along each axis. The output is
        [xmin, xmax, ymin, ymax, zmin, zmax]'''
        limits = [0, 0, 0, 0, 0, 0]
        vertices = self.stl.getAllVertices()
        for vertex in vertices:
            for i in range(3):
                if vertex[i] < limits[i*2]: limits[i*2] = vertex[i]
                if vertex[i] > limits[i*2+1]: limits[i*2+1] = vertex[i]
        return limits

# %%
