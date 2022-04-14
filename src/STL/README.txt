ReadSTL: A module that contains two classes:
  STL: A large container that can parse and distribute the information in an .stl file
  STL_Facet: A container for a single facet in an .stl file.

PlotSTL: A module that contains a single class:
  PlotSTL: Takes an STL object as an input and can handle plotting and transformations for the object.
  
Transform: A module that contains a single class:
  Transform: Creates a transformatin matrix and handles the mathematics for various affine transformations

To use:
Example to get an STL plotted"
  stl = STL("Sample STL Files/House4 106.stl") #Load the STL
  print(stl.toString()) #Check functionally loaded
  StlPlt = PlotSTL(stl) #Create the PlotSTL object
  StlPlt.orthographic("left") #Rotate to left view of STL
  StlPlt.rotate(psi=np.pi/4) #Rotate pi/4 radians around the vertical axis
  StlPlt.moveToFloor() #Lower the STL to the floor
  StlPlt.moveToCenter() #Move the STL to the center of the build plate
  StlPlt.updateSTL() #Load all transformations
  StlPlt.plotSTL() #Plot the STL to the screen
