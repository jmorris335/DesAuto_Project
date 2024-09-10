# STL Slicer

This is a class project undertaken at Clemson University. It's purpose is to visualize STL files and slice them into buildable layers and exportable GCode for a Fused Filament Fabrication (FFF/FDM) 3D printer.

Date: Jan - Apr, 2022
Authors: William Hawthorne, John Morris
Contact: jhmrrs AT clemson DOT edu

https://github.com/user-attachments/assets/1e20b80a-8740-4d0c-ad34-eaecbd1c803d

### To Build Project
You'll have to build the project if you want to distribute it. Building is OS specific, so it will only work on the OS of the computer you build on, but then it can be shared as an executable to anyone running that OS.

1. Make sure you have pyinstaller installed using pip.

2. Run ```pyinstaller cli.spec``` into the terminal. This will create a ```dist``` directory that will contain the single executable.

3. Note that the project will follow the path in ```cli.py```, which calls ```src/__main__.py```.
