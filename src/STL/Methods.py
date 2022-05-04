import numpy as np

''' A collection of methods. 

Note that this class does not rely on imports of any relative classes (anything 
in the STL package) and therefore can be inherited by any of them.
'''

def checkSimilarTuples(tuple1, tuple2, tol=0.01):
    ''' Checks if the coordinates of the two tuples are within a certain tolerance
    of each other.'''
    if tuple1 == tuple2: return True
    if len(tuple1) != len(tuple2): return False
    err = 0
    for i in range(len(tuple1)):
        err += abs(tuple1[i] - tuple2[i])
    return err <= tol

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

def isOutOfBounds(coords: list, start, end):
    ''' Checks if any of the inputted coordinates are outside the boundary
    defined by start, end.'''
    for coord in coords:
        if (coord > start) & (coord < end): return False
    return True

def normalizeVector(vector):
    ''' Normalizes the vector by dividing element-wise by the maximum value
    in the vector'''
    a = abs(max(vector))
    if a == 0: out = [0., 0., 0.]
    else: out = [i/a for i in vector]
    return out

def sumVectors(vectors: list):
    ''' Element wise vector summation.'''
    vector_size = len(vectors[0])
    out = [0] * vector_size
    for i in range(vector_size):
        out[i] = sum(vector[i] for vector in vectors)
    return out

def safeAppend(pointslist: list, pnt):
    ''' Appends the pnt to pointslist if the pnt is not previously found in pointslist'''
    for point in pointslist:
        if checkSimilarTuples(point, pnt):
            return pointslist
    pointslist.append(pnt)
    return pointslist

def euclidianDistance(pnt1, pnt2):
    ''' Returns the euclidian (geometric) distance between the two points.'''
    distance = 0
    for i in range(min([len(pnt1), len(pnt2)])):
        distance += (pnt2[i] - pnt1[i]) ** 2
    return distance ** (1/2)

def horizontalIntersectsLineSeg(y, line_seg: list):
    ''' Returns True if the line at y(x) = y intersects the segment line_seg. Returns
    False for no intersection, or collinearity.'''
    a = line_seg[0]
    b = line_seg[1]
    if a[1] == b[1]: return False
    if a[1] >= y:
        if b[1] <= y: return True
    elif b[1] >= y: return True
    return False

def verticalIntersectsLineSeg(x, line_seg: list):
    ''' Returns True if the vertical line at x = x intersects the segment line_seg. 
    Returns False for no intersection, or collinearity.'''
    a = line_seg[0]
    b = line_seg[1]
    if a[0] == b[0]: return False
    if a[0] >= x:
        if b[0] <= x: return True
    elif b[0] >= x: return True
    return False

def orderPoints(points: list):
    ''' Orders points from least to greatest, starting with the x coordinate, then
    the y coordiante, then the z coordinate.'''
    if points == None or len(points) <= 1:
        return points
    a = list()
    for i in range(len(points)): a.append(tuple(points[i]))
    dtype = list()
    size = range(len(a[0]))
    for i in size: dtype.append((str(i), float))
    order=[str(i) for i in size]
    out = np.sort(np.array(a, dtype=dtype), order=order)
    return out.tolist()

def sortByOrderedSet(toSort: list, toMatch: list, original: list):
    ''' Sorts the list toSort by a set of indicies derived from comparing toMatch
    with original. Each entry in toMatch is located in original, which corresponds
    to the base location of the entry in toSort. The output is toSort, sorted with
    the changes from original to toMatch.'''
    out = list()
    for pnt in original:
        index = toMatch.index(pnt)
        out.append(toSort[index])
    return out

def NormalSign(vector, is_horizontal: True):
    ''' Returns the sign element in the vector. Returns 0 if the coordinate is 0.'''
    if is_horizontal: a = vector[0]
    else: a = vector[1]
    if a == 0: return 0
    return abs(a) / a

def calculateNormal(pnt1, pnt2, pnt3):
    ''' Returns the normal to the plane composed of the 3 inputted points.
    The points should be oriented CCW to each other (following the RH Rule).
    Note that the returned vector is normalized.'''
    q = np.array(pnt1)
    r = np.array(pnt2)
    s = np.array(pnt3)
    qr = q - r
    qs = q - s
    out = np.cross(qr, qs)
    if max(out) == 0: return out
    return out / max(out)
    