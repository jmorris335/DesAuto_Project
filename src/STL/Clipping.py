import numpy as np

from STL.ReadSTL import STL, STL_Facet

def clipping(stl: STL, windowSize : tuple):
    """
    Clips the triangles in self to the given window
    Input: windowSize: should contain the (x, y, z) dimmensions of the window
    Output: newSTL: new STL object of the clipped original object
    """
    
    debugIter = 0
    ogSTL = stl
    newSTL = stl

    def addFace(face: STL_Facet):
        #subfunction to add a new face to the existing STL or make a new one if one hasn't been made yet
        if (newSTL is ogSTL):
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

        
    for face in ogSTL.getFacets():
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
            newSTL = addFace(face)
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
                newSTL = addFace(face)
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
                    newSTL = addFace(face)

    return newSTL
