import copy

class STL_Facet:
    def __init__(self, normal: list, vertices: list):
        ''' A single face on an STL object.
        
        Inputs
        ---
        normal : [1x3] list
            The x, y, z coordinates for the normal vector of the face
        vertices : [nx[1x3]] list
            The vertices of each point comprising the facet. If the face
            is a triangle, then "n" will be 3. Each entry in "vertices" 
            is a [1x3] list of the x, y, z coordinates for that point.
        '''
        self.normal = normal
        self.vertices = vertices
        self.num_vertices = len(self.vertices)

    # Modifiers
    def loadFromMatrix(self, A):
        ''' Sets the normal vector and vertices according to the inputted matrix.
        
        Inputs
        ---
        A : [n+1 x 4] or [n+1 x 3] list or np.array
            A matrix where the first row corresponds to the normal vector and each
            successive row corresponds to a vertex. Each row can either be in traditional
            or homogenized coordinates. In homogenized, a row would be [x_val, y_val, z_val, 1]

        Example: A = [[0, 0, 1, 1], [0, 0, 0, 1], [1, 0, 0, 1], [0, 1, 0, 1]]
        '''
        self.normal = A[0][0:3]
        for row in range(1, len(A)):
            self.vertices[row-1] = A[row][0:3]

    # Access Functions
    def copyVertices(self):
        ''' Returns a list of the vertices that does not reference the actual class member'''
        return copy.deepcopy(self.vertices)
    
    def vertex(self, index):
        ''' Returns the vertex at the given index. Note the first index is 0.'''
        return self.vertices[index]
    
    def getMatrix(self):
        ''' Returns the normal vector and vertices for the face as a [nx4] matrix suitable
        for transformations in a homogenized coordinate system.'''
        matrix = list()
        matrix.append(self.homogenize(self.normal))
        for vertex in self.vertices:
            matrix.append(self.homogenize(vertex))
        return matrix

    def getXCoordinates(self):
        ''' Returns a list of the x coordinates for each point in the face.'''
        x = list()
        for vertex in self.vertices: x.append(vertex[0])
        return x

    def getYCoordinates(self):
        ''' Returns a list of the y coordinates for each point in the face.'''
        y = list()
        for vertex in self.vertices: y.append(vertex[1])
        return y

    def getZCoordinates(self):
        ''' Returns a list of the z coordinates for each point in the face.'''
        z = list()
        for vertex in self.vertices: z.append(vertex[2])
        return z

    # Service Functions
    def homogenize(self, l):
        ''' Adds a homogenized coordinate (1) to the [1x3] vector'''
        vector = copy.deepcopy(l)
        vector.append(1)
        return vector

    def toString(self):
        return str(self.getMatrix())


class STL:
    def __init__(self, file=None):
        ''' Contains an STL object, which can include the STL file, or a collection of 
        facets that define the object.
        
        Inputs
        ---
        file: str
            The name of the file (with extension), example: "Cube 432.stl"

        Examples
        ---
        Read in the file:
        ```
            from ReadSTL import STL

            cube = STL("Cube 432.stl")
            print(cube.facets[0].toString())
        ```
        '''
        if file != None: self.parseFile(file)
            
    # Handling
    def parseFile(self, file):
        ''' Parses a .stl file and creates a reachable object containing the facets
        (faces) contained in the file.'''
        self.file = file
        self.lines = self.readFile()
        self.name = self.getNameOfSolid()
        self.faces = self.getFacets()

    def emptyCopy(self, facet: STL_Facet=None):
        ''' Creates a new STL but does not parse the file. Optionally can append a single
        facet to the new STL's faces list.'''
        out = STL(None)
        out.name = self.name
        out.file = self.file
        out.faces = list()
        if facet != None:
            out.faces.append(facet)
        return out

    # Access
    def num_faces(self):
        ''' Returns the number of faces in the object''' 
        return len(self.faces)

    def getAllVertices(self):
        ''' Returns a list containing all vertices in the object.
        This is not guaranteed to not contain duplicates'''
        out = list()
        for face in self.faces:
            for vertex in face.vertices:
                out.append(vertex)
        return out

    def toString(self):
        ''' Prints the name of and number of faces in the object '''
        return self.name + ", Number of Faces: " + str(self.num_faces())

    # Process File
    def readFile(self):
        ''' Opens the files and returns all the lines in the files as a
        list of strings'''
        with open(self.file, 'r') as file:
            lines = file.readlines()
        return lines
    
    def getNameOfSolid(self):
        ''' Returns the name of the solid object in the .stl file'''
        str = self.lines[0]
        firstCharInd = str.find(" ") + 2
        lastCharInd = str.find(" ", firstCharInd)
        name = str[firstCharInd : lastCharInd]
        return name

    def getFacets(self):
        ''' Finds and returns all the facets in the .stl file as a list of 
        STL_Facet objects'''
        facet_indices = self.getFacetIndices()
        facets = list()
        for index in facet_indices:
            try: facet_loop = self.getFacetLoop(index)
            except: return
            else: facets.append(self.parseFacetLoop(facet_loop))
        return facets

    def getFacetIndices(self):
        ''' Returns indices to all the lines that begin a new facet (containing
        the phrase "facet Normal"'''
        facet_indices = list()
        for i in range(len(self.lines)):
            if self.lines[i].find("facet normal") != -1:
                facet_indices.append(i)
        return facet_indices

    def getFacetLoop(self, index: int):
        ''' Returns the set of lines starting the inputted "index" and corresponding
        to a single facet in the .stl file'''
        facet_loop = list()
        line = self.lines[index]
        while line.find("endfacet") == -1:
            facet_loop.append(line)
            index += 1
            line = self.lines[index]
        return facet_loop

    def parseFacetLoop(self, facet_loop: list):
        ''' Returns the normal vector and verticies contained in the facet_loop'''
        normal = self.getNormal(facet_loop)
        vertices = self.getVertices(facet_loop)
        return STL_Facet(normal, vertices)

    def getNormal(self, facet_loop: list):
        ''' Returns the normal vector in the inputted facet lines'''
        normal = list()
        line = facet_loop[0]
        return self.getFloatsFromString(line)

    def getVertices(self, facet_loop: list):
        ''' Returns the vertices contained in the inputted facet lines'''
        vertices = list()
        index = 2
        line = facet_loop[index]
        while line.find("endloop") == -1:
            vertices.append(self.getFloatsFromString(line))
            index += 1
            line = facet_loop[index]
        return vertices

    def getFloatsFromString(self, line: str):
        ''' Returns a list containing all the floats in the inputted string ("line")
        that are seperated by spaces'''
        out = list()
        words = self.getTextBetweenSpaces(line)
        for word in words:
            try: coord = float(word)
            except ValueError: continue
            else: out.append(coord)
        return out

    def getTextBetweenSpaces(self, line: str):
        ''' Returns a list of all the words in the inputted string ("line") 
        that are seperated by spaces'''
        out = list()
        indices = [i for i in range(len(line)) if line.startswith(" ", i)]
        indices.append(len(line))
        for i in range(len(indices)-1):
            try:
                word = line[indices[i] : indices[i+1]]
            except: continue
            else: out.append(word)
        return out

    # Clipping
    def clipping(self, windowSize : tuple):
        """
        Clips the triangles in self to the given window
        Input: windowSize: should contain the (x, y, z) dimmensions of the window
        Output: newSTL: new STL object of the clipped original object
        """
        
        import numpy as np

        newSTL = self

        def addFace():
            #subfunction to add a new face to the existing STL or make a new one if one hasn't been made yet
            if (newSTL is self):
                return STL.emptyCopy(facet = face)
            else:
                return newSTL.faces.append(face)

        def CS(p1):
            #Store Cohen-Sutherland values in 4th index
            if (p1[0] < 0): p1[3] += 1
            elif (p1[0] > windowSize[0]): p1[3] += 2
            if (p1[1] < 0): p1[3] += 4
            elif (p1[1] > windowSize[1]): p1[3] += 8
            if (p1[2] < 0): p1[3] += 16
            elif (p1[2] > windowSize[2]): p1[3] += 32
            return p1


        def pushPoints(push, dir1, dir2, iter = 0):
            #recursive subfunction that pushes the "push" value into the viewing window in the direction of the points dir1 and dir2. Iter is used to determine which viewing window plane to push into

            if (push[3] == 0):
                return

            newx1 = newx2 = np.array(push)[0:3]
            x1 = np.array(dir1)[0:3]
            x2 = np.array(dir2)[0:3]

            m1 = (x1 - newx1)
            m2 = x2 - newx2

            nAll = np.array([[0, 0, 1], [1, 0, 0],[0, 1, 0]])
            n = nAll[iter%3]

            if (newx1[iter%3] < 0):
                p01 = p02 = np.zeros(3)
            elif(newx1[iter%3] > windowSize[iter%3]):
                p01 = p02 = np.array(windowSize)
            else:
                if(m1[iter%3] < 0):
                    p01 = np.zeros(3)
                else:
                    p01 = np.array(windowSize)
                if(m2[iter%3] < 0):
                    p02 = np.zeros(3)
                else:
                    p02 = np.array(windowSize)


            if (m1.dot(n) != 0):
                d = ((p01 - newx1).dot(n))/m1.dot(n)
                if (0 < d < 1):
                    newx1 = newx1 + m1 * d
                    newx1.tolist().append(0)
                    newx1 = CS(newx1)

            if (m2.dot(n) != 0):
                d = ((p02 - newx2).dot(n))/m2.dot(n)
                if (0 < d < 1):
                    newx2 = newx2 + m2 * d
                    newx2.tolist().append(0)
                    newx2 = CS(newx2)

            #recursion to keep pushing until all points are within the viewing window
            newPoints = []

            if(newx1 == push or newx2 == push):
                    newPoints.extend(pushPoints(push, x1, x2, iter=iter+1))
            else:
                if (newx2[3] != 0):
                    newPoints.extend(pushPoints(newx2, x2, newx1, iter=iter+1))
                else:
                    newPoints.append(newx2)
                if (newx1[3] != 0):
                    newPoints.extend(pushPoints(newx1, x1, newx2, iter=iter+1))
                else:
                    newPoints.append(newx1)

            return newPoints
            
            
        for face in self.getFacets():
            verts = face.copyVertices()
            p1 = verts[0]
            p2 = verts[1]
            p3 = verts[2]
            if (len(p1) < 4):
                p1.append(0)
                p2.append(0)
                p3.append(0)

            
            #check for clipping and push

            if ((0 < min([p1[0],p2[0],p3[0]])) and (max([p1[0],p2[0],p3[0]]) < windowSize[0]) and \
                (0 < min([p1[1],p2[1],p3[1]])) and (max([p1[1],p2[1],p3[1]]) < windowSize[1]) and \
                (0 < min([p1[2],p2[2],p3[2]])) and (max([p1[2],p2[2],p3[2]]) < windowSize[2])):
                newSTL = addFace()
                continue
            elif(max([p1[0],p2[0],p3[0]]) < 0 or min([p1[0],p2[0],p3[0]]) > windowSize[0] or \
                 max([p1[1],p2[1],p3[1]]) < 0 or min([p1[1],p2[1],p3[1]]) > windowSize[1] or \
                 max([p1[2],p2[2],p3[2]]) < 0 or min([p1[2],p2[2],p3[2]]) > windowSize[2]):
                 continue
            else:
                p1 = CS(p1)
                p2 = CS(p2)
                p3 = CS(p3)
                if (p1[3] == p2[3] == p3[3] == 0):
                    newSTL = addFace()

                else:
                    if (p1[3] != 0):
                        verts.remove(p1)
                        verts.append(pushPoints(p1, p2, p3))
                    if (p2[3] != 0):
                        verts.remove(p2)
                        verts.append(pushPoints(p2, p1, p3))
                    if (p3[3] != 0):
                        verts.remove(p3)
                        verts.append(pushPoints(p3, p1, p2))

                    for i in range(1, len(verts)%3 + 2):
                        Q = np.array(verts[0])
                        R = np.array(verts[i])
                        S = np.array(verts[i+1])
                        QR = R - Q
                        QS = S - Q
                        normal = np.cross(QR, QS).toList()
                        face = STL_Facet(normal, [verts[0], verts[i], verts[i+1]])
                        newSTL = addFace()

        return newSTL

# %%


