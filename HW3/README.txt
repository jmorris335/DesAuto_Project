The class should be viable for work going forward if we want to use it for the project. 

A typical call using the Transform class to translate and rotate <A> to <Aprime> looks like this:
T = Transform()
A = <Nx4 Array>
T.rotateInPlace(theta= np.pi/2)
T.translate(dely= 2)
Aprime = T.transform(A)
