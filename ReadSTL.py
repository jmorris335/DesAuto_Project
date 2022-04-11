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

    def vertex(self, index):
        ''' Returns the vertex at the given index. Note the first index
        is 0.'''
        return self.vertices[index]
    
    def getMatrix(self):
        ''' Returns the vertices for the face as a [nx4] matrix suitable
        for transformations in a homogenized coordinate system.'''
        matrix = list()
        for vertex in self.vertices:
            row = vertex
            row.append(1)
            matrix.append(row)
        return matrix

    def getXCoordinates(self):
        ''' Returns a list of the x coordinates for each point in the face.'''
        x = list()
        for vertex in self.vertices:
            x.append(vertex[0])
        return x

    def getYCoordinates(self):
        ''' Returns a list of the y coordinates for each point in the face.'''
        y = list()
        for vertex in self.vertices:
            y.append(vertex[1])
        return y

    def getZCoordinates(self):
        ''' Returns a list of the z coordinates for each point in the face.'''
        z = list()
        for vertex in self.vertices:
            z.append(vertex[2])
        return z

    def toString(self):
        return str(self.getMatrix())


class STL(object):
    def __init__(self, file):
        ''' Parses a .stl file and creates a reachable object containing the facets
        (faces) contained in the file
        
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
        self.file = file
        self.lines = self.readFile()
        self.name = self.getNameOfSolid()
        self.faces = self.getFacets()

    # Access
    def num_faces(self):
        ''' Returns the number of faces in the object''' 
        return len(self.facets)

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
        lastCharInd = str.find(" ", firstCharInd) - 1
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

    # Plot STL







