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
        debugIter = 0
        newSTL = self

        def addFace():
            #subfunction to add a new face to the existing STL or make a new one if one hasn't been made yet
            if (newSTL is self):
                return STL.emptyCopy(newSTL, facet = face)
            else:
                newSTL.faces.append(face)
                return newSTL

        def CS(p1):
            #Store Cohen-Sutherland values in 4th index
            if (p1[0] < 0): p1[3] += 1
            elif (p1[0] > windowSize[0]): p1[3] += 2
            if (p1[1] < 0): p1[3] += 4
            elif (p1[1] > windowSize[1]): p1[3] += 8
            if (p1[2] < 0): p1[3] += 16
            elif (p1[2] > windowSize[2]): p1[3] += 32
            return p1


        def pushPoints(p0, p1, iter):
            #recursive function that pushes p0 in the direction of p1 until it is within the viewing window
            """
            Inputs:
            p0 = numpy vector of a point that needs to be pushing inbounds
            p1 = numpy vector of a point that defines the direction of push
            iter = iterator that represents which dimmension we're focusing on (x, y, z)
            
            Outputs:
            a numpy vector
            """
            if (p0[3] == 0):
                return p0
            iter = iter % 3
            newp = p0[0:3]
            dir = p1[0:3]
            m = dir - newp
            n = np.array([[1, 0, 0],[0, 1, 0],[0, 0, 1]])[iter]

            if (newp[iter] < 0):
                p01 = np.zeros(3)
            elif (newp[iter] > windowSize[iter]):
                p01 = np.array(windowSize)
            else:
                if (m[iter] < 0):
                    p01 = np.zeros(3)
                else:
                    p01 = np.array(windowSize)

            if (m.dot(n) != 0):
                d = ((p01 - newp).dot(n))/m.dot(n)
                if (0 < d <= 1):
                    newp = newp + m * d
            newp = CS(np.hstack([newp, 0]))
            return newp


        def uniqueRowOrdered(arr):
            #takes input numpy array and outputs new numpy array without duplicates, removing the second duplicate
            newArr = []
            arr = arr.tolist()
            for row in arr:
                if row not in newArr:
                    newArr.append(row)
            return np.array(newArr)

            
            
        for face in self.getFacets():
            debugIter += 1
            verts = face.copyVertices()
            p1 = verts[0]
            p2 = verts[1]
            p3 = verts[2]
            if (len(p1) < 4):
                p1.append(0)
                p2.append(0)
                p3.append(0)

            
            #check if the face is entirely inside or outside the viewing window

            if ((0 <= round(min([p1[0],p2[0],p3[0]])), 8) and (round(max([p1[0],p2[0],p3[0]]), 8) <= windowSize[0]) and \
                (0 <= round(min([p1[1],p2[1],p3[1]])), 8) and (round(max([p1[1],p2[1],p3[1]]), 8) <= windowSize[1]) and \
                (0 <= round(min([p1[2],p2[2],p3[2]])), 8) and (round(max([p1[2],p2[2],p3[2]]), 8) <= windowSize[2])):
                newSTL = addFace()
                continue
            elif(round(max([p1[0],p2[0],p3[0]]), 8) < 0 or round(min([p1[0],p2[0],p3[0]]), 8) > windowSize[0] or \
                 round(max([p1[1],p2[1],p3[1]]), 8) < 0 or round(min([p1[1],p2[1],p3[1]]), 8) > windowSize[1] or \
                 round(max([p1[2],p2[2],p3[2]]), 8) < 0 or round(min([p1[2],p2[2],p3[2]]), 8) > windowSize[2]):
                 continue
            else:
                p1 = CS(p1)
                p2 = CS(p2)
                p3 = CS(p3)
                if (p1[3] == p2[3] == p3[3] == 0):
                    newSTL = addFace()
                else:
                    
                    #push points one at a time in one direction at a time and create new faces to add to the stl
                    length = 3
                    vertArray = np.array(verts)
                    i = j = 0 #i is for indexing the vertices, j is to prevent infinite while loop
                    while ( i//length < 3 and j < 100 and any(vertArray[:,3] !=0)):
                        length = len(vertArray)
                        iter = i % length
                        if (vertArray[iter,3] != 0):
                            if (iter == 0):
                                newPoints = np.vstack([pushPoints(vertArray[0,:], vertArray[-1,:], i//length), pushPoints(vertArray[0,:], vertArray[1,:], i//length)])
                                vertArray = np.vstack([vertArray[1:length], newPoints])
                                i = i - 1
                            elif((i % length) == (length - 1)):
                                newPoints = np.vstack([pushPoints(vertArray[iter,:], vertArray[iter - 1,:], i//length), pushPoints(vertArray[iter,:], vertArray[0,:], i//length)])
                                vertArray = np.vstack([vertArray[0:length - 1], newPoints])
                            else:
                                newPoints = np.vstack([pushPoints(vertArray[iter,:], vertArray[iter - 1,:], i//length), pushPoints(vertArray[iter,:], vertArray[iter + 1,:], i//length)])
                                vertArray = np.vstack([vertArray[0:iter], newPoints, vertArray[iter + 1:length]])
                                
                            vertArray = uniqueRowOrdered(vertArray)
                        
                        i = (i + 1)
                        
                        j += 1
                    
                    
                    #skip non-triangles
                    vertArray = vertArray[vertArray[:,3] == 0, 0:3]
                    if (len(vertArray) < 3):
                        continue
                    
                    #calculate normal (which should be the same for each new triangle in the polygon)
                    verts = vertArray.tolist()
                    Q = np.array(verts[0])
                    R = np.array(verts[1])
                    S = np.array(verts[2])
                    QR = R - Q
                    QS = S - Q
                    normal = np.cross(QR, QS)
                    normal = np.around(normal / (np.sqrt(normal.dot(normal))), decimals = 6) #normalizes vector
                    normal = normal.tolist()

                    #create the new faces and add them to the new STL that gets outputed
                    for i in range(1, len(verts)%3 + 2):
                        face = STL_Facet(normal, [verts[0], verts[i], verts[i+1]])
                        newSTL = addFace()

        return newSTL

# %%


