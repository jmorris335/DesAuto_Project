from copy import deepcopy
from math import floor, ceil
from ReadSTL import STL, STL_Facet as Facet

class Edge:
    def __init__(self, pnt1, pnt2, normal):
        ''' An edge is a line segment terminated by two points with a single
        normal vector describing which direction is out.'''
        self.pnt1 = pnt1
        self.pnt2 = pnt2
        self.normal = normal

class Hull:
    ''' A closed profile composed of line segments'''
    def __init__(self, points, normals):
        self.pnts = points
        self.normals = normals

    def getXYZCoordinates(self):
        xcoords = list()
        ycoords = list()
        zcoords = list()
        for point in self.pnts:
            xcoords.append(point[0])
            ycoords.append(point[1])
            zcoords.append(point[2])
        return xcoords, ycoords, zcoords

    #FIXME: Add method for getting offset, using centroid

class Slice:
    def __init__(self, hulls):      
        ''' A collection of hulls that define a slice.
        
        Inputs
        ---
        hulls : list of Hull-type objects
        '''
        self.hulls = hulls
        self.z_datum = hulls[0].pnts[0][0]

    def getXYZCoordinates(self):
        xcoords = list()
        ycoords = list()
        zcoords = list()
        for hull in self.hulls:
            hull_x, hull_y, hull_z = hull.getXYZCoordinates()
            xcoords.extend(hull_x)
            ycoords.extend(hull_y)
            zcoords.extend(hull_z)
        return xcoords, ycoords, zcoords

    #FIXME: Add methods for accessing a certain edge

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
        
        Slicing Process
        ---
        1. Pass the object. Determine number of slices
        2. For each slice:
            1. Find which faces intersect the plane of the slice
            2. Determine the intersection coordinates
            3. Form line segments out of each face intersection
            4. Connect line segments with similar endpoint coordinates into a hull
            5. Form the slice from the list of hulls
        
        Notes
        ---
        1. The plane of the slice is always the bottom of the interval defined by the layer
        height. For instance, if an object's lowest z-coordinate is z = 2.2, then the first
        slice will comprise all the faces that intersect the z = 2.2 plane. 
        2. Slice planes are always parallel to the XY plane
        3. The top of the object, if not a even divisor with the layer height, is also added
        as a slice plane. For instance, if an object with a minimum z-coordinate of z = 0, and
        a maximum z-coordinate of z = 1 has a layer height of 0.3, then there will be 4 slice
        planes at z = [0, .3, .6, .9, 1].
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

    def findFacetsAtDatum(self, facets, z_datum):
        ''' Returns all faces in facets that intersect the plane that is located at the 
        z_datum and is parallel to the XY plane'''
        out = list()
        for face in facets:
            if self.faceIntersectsDatum(face, z_datum):
                out.append(face)
        return out

    # Slicing Functions
    def sliceSTL(self):
        ''' Calling function that forms the slices for each layer, which are accessible
        from the member "slices".'''
        all_unsorted_edges = self.getEdgesForAllSlices()
        for unsorted_edges in all_unsorted_edges:
            hulls = self.makeHulls(unsorted_edges)
            if len(hulls) == 0:
                self.numSlices -= 1
            else:
                self.slices.append(Slice(hulls))

    def getEdgesForAllSlices(self):
        ''' Returns a list of lists, where each entry corresponds to a list of all the edges 
        for each slice.'''
        slices_edges = list()
        for layer_index in range(self.numSlices-1):
            z_datum = self.min_z + (layer_index * self.del_z)
            slices_edges.append(self.getSliceEdges(layer_index, z_datum))
        slices_edges.append(self.getSliceEdges(self.numSlices-1, self.max_z))
        return slices_edges

    def getSliceEdges(self, layer_index, z_datum):
        ''' Returns a list of edges contained in the slice referenced by the 
        layer_index, which corresponds to the plane located at the z_datum.'''
        out = list()
        facets_in_slice = self.facet_groups[layer_index]
        facets_at_datum = self.findFacetsAtDatum(facets_in_slice, z_datum)
        for face in facets_at_datum:
            edges = self.getEdgesFromFace(face, z_datum)
            if edges != None: out.extend(edges)
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
        indices = [i for i in range(len(pnts))]
        indices.append(0)
        for i in range(len(indices)-1):
            pnt1 = pnts[indices[i]]
            pnt2 = pnts[indices[i+1]]
            if self.lineIntersectsDatum(pnt1, pnt2, z_datum):
                temp = self.interpolateZ(pnt1, pnt2, z_datum)
                if temp != None: 
                    intersection_pnts = self.safeAppend(intersection_pnts, temp)
        return intersection_pnts

    def makeHulls(self, edges):
        ''' Finds connected edges to form a list of closed profiles (hulls) comprised of
        the edges passed to the function.'''
        hulls = list()
        edges = deepcopy(edges)
        while len(edges) > 0:
            search_pnt = edges[0].pnt1
            points_in_hull = [search_pnt]
            normals_in_hull = list()
            search_pnt, curr_edge = self.findJoiningPoint(search_pnt, edges)
            
            while search_pnt != None:
                points_in_hull.append(search_pnt)
                normals_in_hull.append(curr_edge.normal)
                edges.remove(curr_edge)
                search_pnt, curr_edge = self.findJoiningPoint(search_pnt, edges)
            
            hulls.append(Hull(points_in_hull, normals_in_hull))
        return hulls

    def findJoiningPoint(self, pnt, edges):
        ''' Parses through edges looking for an edge that has a similar coordinate as
        "pnt". Returns the associated point in the new edge as well as the edge. Returns
        None if it cannot find an similar point.'''
        for edge in edges:
            if self.checkSimilarTuples(pnt, edge.pnt1):
                return edge.pnt2, edge
            elif self.checkSimilarTuples(pnt, edge.pnt2):
                return edge.pnt1, edge
        return None, None
                
    # Service Functions
    def safeAppend(self, pointslist: list, pnt):
        ''' Appends the pnt to pointslist if the pnt is not previously found in pointslist'''
        for point in pointslist:
            if self.checkSimilarTuples(point, pnt):
                return pointslist
        pointslist.append(pnt)
        return pointslist

    @staticmethod
    def lineIntersectsDatum(pnt1, pnt2, z_datum, tol=1e-5):
        ''' Returns true if the line segment connecting pnt1 and pnt2 intersects the 
        plane that is located at z_datum and parallel to the XY plane.'''
        if abs(pnt1[2] - z_datum) <= tol: return True
        if abs(pnt2[2] - z_datum) <= tol: return True        
        if pnt1[2] >= z_datum:
            if pnt2[2] <= z_datum: return True
            else: return False
        if pnt2[2] >= z_datum: return True
        return False

    @staticmethod
    def faceIntersectsDatum(face: Facet, z_datum, tol=1e-5):
        ''' Returns true if the face intersects the plane (even by a vertex) that is
        located at z_datum and parallel to the XY plane.'''
        Zpnts = face.getZCoordinates()
        if abs(min(Zpnts) - z_datum) <= tol: return True
        if abs(max(Zpnts) - z_datum) <= tol: return True
        if min(Zpnts) <= z_datum:
            if max(Zpnts) >= z_datum: return True
        return False

    @staticmethod
    def interpolateZ(pnt1, pnt2, z_datum, tol=1e-5):
        ''' Returns the point on the line corresponding to the z_datum. If the line is 
        contained on the plane parallel to the XY plane and intersecting the z_datum, 
        then the function returns the first point. If the line does not intersect the 
        plane then the function returns None.'''
        m = list()
        for i in range(len(pnt1)): m.append(pnt2[i] - pnt1[i])
        if abs(m[2]) <= tol: return None
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