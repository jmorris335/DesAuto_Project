from STL.ReadSTL import STL, STL_Facet
import STL.Methods as mthd
import numpy as np

'''Set of functions for generating an offset.

Status: Currently these functions produce singular matrix values that are ill-suited
for offsetting. Work needs to be done to identify this problem. -JM, 5 May 2022
'''
def getOffsetSTL(stl: STL, offset):
    ''' Returns a similar STL where each point has been offset by the specified value.
    Negative offset values result in inwards (reduced) offsets.'''
    out = stl.emptyCopy()
    for face in stl.faces:
        out_pnts = list()
        for pnt in face.vertices:
            dir = getOffsetDistance(stl, pnt, offset)
            out_pnts.append(mthd.sumVectors([pnt, dir]))
            #FIXME: Delete
            for pnt in out_pnts[-1]:
                if pnt > 1e9: print(dir)
            # Delete Above
        out.faces.append(STL_Facet(face.normal, out_pnts))
    return out

def getOffsetDistance(stl: STL, point, offset):
    ''' Finds the direction of offsetting for a specified point by taking the sum of 
    the normalized normals for all the edges connected to the point.'''
    vector = getOffsetVector(stl, point)
    dir = mthd.normalizeVector(vector)
    dir = [dir[i] * offset for i in range(len(dir))]
    return dir

def getOffsetVector(stl: STL, point):
    ''' Returns the vector off the displacement of the point.'''
    normals = getConnectedNormals(stl, point)
    normals = mthd.cleanDuplicates(normals, .2)
    weights = calculateOffsetWeights(normals)
    if weights[0] == None:
        return mthd.sumVectors(normals)
    else: return calculateWeightedVector(weights, normals)

def calculateWeightedVector(weights, normals):
    ''' Calculates the weighted vector.'''
    temp = list()
    for i in range(len(normals)):
        temp.append([normals[i][j] * weights[i] for j in range(len(normals[i]))])
    out = averageVectors(temp)
    return out

def getConnectedNormals(stl: STL, point):
    ''' Returns a list of the normals for all faces that contain the specifed point'''
    out = list()
    for face in stl.faces:
        for pnt in face.vertices:
            if mthd.checkSimilarTuples(pnt, point):
                out.append(face.normal)
                continue
    out = mthd.cleanDuplicates(out)
    return out

def calculateOffsetWeights(normals: list):
    ''' Calculates weighted average for offset norms according to
    https://www.emerald.com/insight/content/doi/10.1108/13552540310477436/full/html
    '''
    matrix = list()
    for i in range(len(normals)):
        row = list()
        for j in range(len(normals)):
            row.append(np.dot(normals[i], normals[j]))
        matrix.append(row)
    matrix = np.array(matrix)
    try: out = np.linalg.solve(matrix, np.ones(len(matrix)))
    except np.linalg.LinAlgError:
        return [None]
    return out

def averageVectors(vectors: list):
    ''' Returns the average of the vectors.'''
    l = len(vectors[0])
    sum = mthd.sumVectors(vectors)
    out = [sum[i] / l for i in range(l)]
    return out
