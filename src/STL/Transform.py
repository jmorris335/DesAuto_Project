"""
Class: Transform
Author: John Morris
Date: 21 Feb 2022
Purpose: Creates a transformation matrix that can perform several transformations via function call
Copyright (C) 2022
"""

import numpy as np
import copy

class Transform:
    ''' Public member is a matrix that can be manipulated using various explicit transformations.
    After all transformations have been called, a Nx4 array can be transformed along the same path by 
    calling transform(<array>)

    Notes
    ---
    The class retains memory after transformation. Clear the matrix by calling the constructor.
    '''
    def __init__(self, orientation=[0, 0, 0], centroid=[0, 0, 0]):
        ''' Constructor for Transform class
        
        Inputs
        ---
        orientation : [float, float, float], default: [0, 0, 0]
            The orientation of the initial view of the object as deviations from the front view,
            defined by rotations of [theta, phi, psi] around the x axis (theta), y axis (phi), 
            and z axis (psi), where the input is [theta, phi, psi]. For an object already oriented 
            in the front view all angles should be zero (the default argument).
        centroid : [float, float, float], default: [0, 0, 0]
            The geometric centroid of the object in distance from the origin of the coordinate
            system.
        '''
        self.T = np.identity(4)
        self.Tsub = np.identity(4)

        self.orig_orientation = orientation
        self.curr_orientation = list()
    
        self.orig_centroid = centroid
        self.curr_centroid = copy.deepcopy(centroid)

    def updateT(self):
        ''' Updates "T" based on changes in "Tsub", then clears "Tsub"

        Notes
        ---
        Private function for setting "T" that prevents "T" from being lost during 
        transformation calls'''
        self.T = np.dot(self.T, self.Tsub)
        self.updateCentroid(self.Tsub)
        self.Tsub = np.identity(4)

    def transform(self, A):
        ''' Transforms matrix "A" by the matrix "T", which must be updated prior to 
        calling. If T is not updated, then A remains unchanged. A is always normalized
        by s (accessed at A[3]) to reference scaling. 
        
        Inputs
        ---
        A : 4x1 np.array
            Array with coordinates for a point as [x, y, z, s]
        
        Output
        ---
        Aprime : np.array
            The product of A with T
        '''
        A = A @ self.T
        rows, col = A.shape
        for row in range(rows):
            s = A[row, 3]
            if s != 1 and s != 0:
                A[row] = [el / s for el in A[row,:]]
        return A

    def transformNorm(self, normal):
        ''' Transforms the normal vector following the equation: 
        n' = n * transpose(inv(T)). For more information see:
        https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/geometry/transforming-normals
        
        Input
        ---
        normal : (1x3) list or tuple
            The normal to be transformed. 
        '''
        Tnorm = np.linalg.inv(self.T).T
        if type(normal) == tuple: normal = list(normal)
        normal.append(1)
        out = normal @ Tnorm
        return out.tolist()[0:3]

    def updateOrientation(self, vector: tuple):
        ''' Log a change to the orientation of the object'''
        if len(vector) != 3:
            raise Exception("Orientation vector passed to vector that was not size 3")
        self.curr_orientation.append(vector)

    def updateCentroid(self, T):
        ''' Update the centroid after a rotation by multiplying by "T"'''
        temp = copy.deepcopy(self.curr_centroid)
        temp.append(1)
        temp = np.array(temp)
        temp = np.dot(temp, T)
        self.curr_centroid = np.ndarray.tolist(temp[0:3])

    ## Rotation
    def rotateAroundX(self, theta):
        ''' Rotate around the x-axis by theta radians, RHS'''
        self.Tsub[1, 1] = np.cos(theta)
        self.Tsub[1, 2] = -np.sin(theta)
        self.Tsub[2, 1] = np.sin(theta)
        self.Tsub[2, 2] = np.cos(theta)
        self.updateOrientation((theta, 0, 0))
        self.updateT()

    def rotateAroundY(self, phi):
        ''' Rotate around the y-axis by phi radians, RHS'''
        self.Tsub[0, 0] = np.cos(phi)
        self.Tsub[0, 2] = -np.sin(phi)
        self.Tsub[2, 0] = np.sin(phi)
        self.Tsub[2, 2] = np.cos(phi)
        self.updateOrientation((0, phi, 0))
        self.updateT()

    def rotateAroundZ(self, psi):
        ''' Rotate around the z-axis by psi radians, RHS'''
        self.Tsub[0, 0] = np.cos(psi)
        self.Tsub[0, 1] = np.sin(psi)
        self.Tsub[1, 0] = -np.sin(psi)
        self.Tsub[1, 1] = np.cos(psi)
        self.updateOrientation((0, 0, psi))
        self.updateT()

    def rotate(self, theta: float=0., phi: float=0., psi: float=0.,
                     x: float=0., y: float=0., z: float=0.):
        ''' Rotates along primary axis offset by x, y, z
        
        Notes
        ---
        The order of rotation is around the x axis, then y axis, then z axis. Function
        calls with multiple rotations must follow this order. To rotate in a different
        order, call the function multiple times with a single rotation per function call.
        '''
        if x != 0 or y != 0 or z != 0: self.translate(-x, -y, -z)
        if theta != 0: self.rotateAroundX(theta)
        if phi != 0: self.rotateAroundY(phi)
        if psi != 0: self.rotateAroundZ(psi)
        if x != 0 or y != 0 or z != 0: self.translate(x, y, z)

    def rotateInPlace(self, theta: float=0., phi: float=0., psi: float=0.):
        ''' Rotates along a coordinate system centerd at the centroid of the object
        
        Notes
        ---
        The order of rotation is around the x axis, then y axis, then z axis. Function
        calls with multiple rotations must follow this order. To rotate in a different
        order, call the function multiple times with a single rotation per function call.
        '''
        init_centroid = copy.deepcopy(self.curr_centroid)
        self.rotate(theta, phi, psi, init_centroid[0], init_centroid[1], init_centroid[2])

    def rotateToOriginal(self):
        ''' Rotates back to the original orientation. The original orientation defaults 
            to the orientation when T was created, but can be changed by calling 
            T.orig_orientation
        '''
        for rotation in reversed(self.curr_orientation):
            self.rotateInPlace(psi=-rotation[2])
            self.rotateInPlace(phi=-rotation[1])
            self.rotateInPlace(theta=-rotation[0])
        self.curr_orientation = list()

    def rotateToFront(self):
        ''' Rotates back to a primary rotation, based on reversing the rotation called
            specified by "orig_orientation"
        '''
        self.rotateToOriginal()
        if self.orig_orientation != [0, 0, 0]:
            self.rotateAroundZ(-self.orig_orientation[2])
            self.rotateAroundY(-self.orig_orientation[1])
            self.rotateAroundX(-self.orig_orientation[0])


    ## Translation
    def translate(self, delx: float=0, dely: float=0, delz: float=0):
        ''' Translate along the 3 axes by the parameters'''
        self.Tsub[3, 0] = delx
        self.Tsub[3, 1] = dely
        self.Tsub[3, 2] = delz
        self.updateT()

    def translateToOrigin(self):
        ''' Translates the coordinates to the origin'''
        self.translate( -self.curr_centroid[0], 
                        -self.curr_centroid[1], 
                        -self.curr_centroid[2])

    def translateToOriginal(self):
        ''' Translates the coordinates to the original centroid. The original centroid
            defaults to the centroid when T was created, but can be changed by calling 
            T.orig_centroid'''
        delx = self.curr_centroid[0] - self.orig_centroid[0]
        dely = self.curr_centroid[1] - self.orig_centroid[1]
        delz = self.curr_centroid[2] - self.orig_centroid[2]
        self.translate(-delx, -dely, -delz)

    ## Scaling
    def scale(self, x=1, y=1, z=1, s=1):
        ''' Scale with all parameters'''
        init_centroid = copy.deepcopy(self.curr_centroid)
        self.translateToOrigin()
        self.Tsub[0, 0] = x
        self.Tsub[1, 1] = y
        self.Tsub[2, 2] = z
        self.Tsub[3, 3] = s
        self.updateT()
        self.translate(init_centroid[0], init_centroid[1], init_centroid[2])

    def scaleSpecific(self, x, y, z):
        ''' Scale along the 3 primary axes'''
        self.scale(x=x, y=y, z=z)

    def scaleGlobal(self, s):
        ''' Scale globally'''
        self.scale(s=1/s)

    ## Shear
    def shear(self, b:float=0, c:float=0, d:float=0, 
                    f:float=0, g:float=0, i:float=0):
        ''' Shear along all primary axes'''
        self.Tsub[0, 1] = b
        self.Tsub[0, 2] = c
        self.Tsub[1, 0] = d
        self.Tsub[1, 2] = f
        self.Tsub[2, 0] = g
        self.Tsub[2, 1] = i
        self.updateT()

    ## Reflections
    def reflectOverXY(self):
        ''' Reflect over XY plane'''
        self.Tsub[2, 2] = -1
        self.updateT()

    def reflectOverYZ(self):
        ''' Reflect over YZ plane'''
        self.Tsub[0, 0] = -1
        self.updateT()

    def reflectOverXZ(self):
        ''' Reflect over XZ plane'''
        self.Tsub[1, 1] = -1
        self.updateT()

    def reflect(self, p, normal):
        ''' Reflect over an arbitrary plane'''
        planeT = Transform(normal, p)
        planeT.translateToOrigin()
        planeT.rotate(-normal[0], -normal[1], -normal[2])
        planeT.reflectOverXY()
        planeT.rotate(normal[0], normal[1], normal[2])
        planeT.translate(p[0], p[1], p[2])
        self.Tsub = planeT.T
        self.updateT()


    ## Orthographic Projection
    def orthographic(self, zero_plane= 'z'):
        ''' Projects the shape onto a 2D plane
        
        Inputs
        ---
        zero_plane : string, default: 'z'
            Specifies the dimension to lose, or normal to the plane of projection. 
            Possible inputs are 'x', 'y', and 'z'
        '''
        if zero_plane == "x": self.Tsub[0, 0] = 0
        elif zero_plane == "y": self.Tsub[1, 1] = 0
        else: self.Tsub[2, 2] = 0
        self.updateT()

    ## Axonometric Projections
    def axonometric(self, phi, theta, zero_plane='z', print=False):
        ''' Projects a trimetric view where fx, fy, and fz are independent
        
        Inputs
        ---
        phi : float
            The rotation over the y axis (initial rotation)
        theta : float
            The rotation over the x axis (follows rotation over y)
        zero_plane : char, default: 'z'
            The normal of the plane to project onto
        print : bool, default: False
            Prints phi, theta, fx, fy, and fz to the screen
        '''
        if print: self.getScaleLengths(phi=phi, theta=theta)
        self.rotateToFront()
        self.rotateInPlace(phi=phi)
        self.rotateInPlace(theta=theta)
        self.orthographic(zero_plane)

    def trimetric(self, fx, fy, zero_plane='z', print=False):
        ''' Projects a trimetric view with fx and fz defined as shown'''
        theta = np.arccos(fy)
        phi = np.sqrt(np.arcsin( (1 - fx**2) / (1 + np.sin(theta)**2) ))
        self.axonometric(phi=phi, theta=theta, zero_plane=zero_plane, print=print)
        
    def dimetric(self, fz, zero_plane='z', print=False):
        ''' Projects a dimetric view where fx is equal to fy'''
        phi = np.arcsin(fz / np.sqrt(2 - fz**2))
        theta = np.arcsin(fz / np.sqrt(2))
        self.axonometric(phi=phi, theta=theta, zero_plane=zero_plane, print=print)

    def isometric(self, zero_plane='z', print=False):
        ''' Projects an 30° isometric view where f is equal to sqrt(2/3)'''
        phi = np.pi/4
        theta = np.arcsin(np.sqrt(1/3))
        self.axonometric(phi=phi, theta=theta, zero_plane=zero_plane, print=print)

    def getScaleLengths(self, phi, theta):
        ''' Prints values for Theta, Phi, Fx, Fy, and Fz to the screen'''
        print("Theta={:.2f} Phi={:.2f}".format(np.rad2deg(theta), np.rad2deg(phi)))
        fx = np.sqrt(np.cos(phi)**2 + (np.sin(phi)**2)*np.sin(theta)**2)
        fy = np.sqrt(np.cos(theta)**2)
        fz = np.sqrt(np.sin(phi)**2 + (np.cos(phi)**2) * np.sin(theta)**2)
        print("Fx={:.2f}".format(fx))
        print("Fy={:.2f}".format(fy))
        print("Fz={:.2f}".format(fz))

    ## Oblique Projections
    def oblique(self, f, alpha, zero_plane='z'):
        ''' Performs a general oblique projection with the front face aligned with 
        the XY plane
        
        Inputs
        ---
        f : float
            The shortening ratio of the receding axis (z)
        alpha : float
            The angle (in radians) the receding axis makes with the horizontal
        zero_plane : char, default: 'z'
            The normal of the plane to project onto
        '''
        self.rotateToFront()
        self.Tsub[2, 0] = -f * np.cos(alpha)
        self.Tsub[2, 1] = -f * np.sin(alpha)
        self.orthographic(zero_plane=zero_plane)

    def cavalier(self, alpha=np.pi/4, zero_plane='z'):
        ''' Performs a cavalier projection onto the XY plane'''
        f = 1/np.tan(np.pi/4)
        self.oblique(f=f, alpha=alpha, zero_plane=zero_plane)

    def cabinet(self, alpha=np.arctan(2), zero_plane='z'):
        ''' Performs a cabinet projection (with 1/2 shortening) onto the XY plane'''
        f = -1/2
        self.oblique(f=f, alpha=alpha, zero_plane=zero_plane)

    ## Perspective Projections
    def perspective(self, p=0, q=0, r=0, s=1):
        ''' Performs a perspective transformation
        
        Input
        ---
        p : float, default=0
            The transformation scale along the x axis
        q : float, default=0
            The transformation scale along the y axis
        r : float, default=0
            The transformation scale along the z axis
        s : float, default=1
            The global scaling factor
        '''
        self.Tsub[0, 3] = p
        self.Tsub[1, 3] = q
        self.Tsub[2, 3] = r
        self.Tsub[3, 3] = s
        self.updateT()

    def triplePointAngular(self, theta, phi, d):
        ''' Performs a triple-point projection onto the XY plane based on
        angular inputs around the x and y axis, with a plane of view located
        d units away from the origin on the z axis
        '''
        p = np.sin(theta) / d
        q = np.cos(theta) * np.sin(phi) / d
        r = np.cos(theta) * np.cos(phi) / d
        self.perspective(p=p, q=q, r=r)

    def triplePoint(self, p=0, q=0, r=0):
        self.perspective(p=p, q=q, r=r)

    def doublePoint(self, p=0, q=0, r=0):
        ''' Performs a double-point projection onto the XY plane
        
        Notes
        ---
        Function parameters allow for specification of any 3 points (where p, q, 
        and r are the distances along the primary axis from the view-plane), however
        double-point projection requires that one of these factors be zero. The
        function will allocate the x-axis distance to be zero if all three factors
        are supplied with values.
        '''
        if p != 0 and q != 0 and r != 0:
            p = 0
        self.perspective(p=p, q=q, r=r)

    def singlePoint(self, d):
        ''' Performs a single-point z-axis projection onto the XY plane'''
        self.perspective(r=1/d, s=1)

    def singlePointAtOrigin(self, d):
        ''' Performs a single-point z-axis projection onto the XY plane, after translating
        the object to the origin (symmetrical projection)
        '''
        init_centroid = copy.deepcopy(self.curr_centroid)
        self.translateToOrigin()
        self.singlePoint(d=d)
        self.translate(init_centroid[0], init_centroid[1], init_centroid[2])

    ## Utility Functions
    def print(self):
        ''' Prints the matrix "T" to the screen'''
        print(self.T)
