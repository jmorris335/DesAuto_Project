# Team 6 FFF Slicer

This is a class project undertaken by students at Clemson University. It's purpose is to take STL files and output GCode to a FFF (Fused Filament Fabrication, AKA FDM) printer. 

Date: Jan - Apr, 2022
Authors: William Hawthorne, John Mcadams, John Morris, Rishikesh Reddy Patlolla

## Setup Instructions
This package is setup to be able to be installed using pip, however, it is not necessary to do so. 

Using Git:
1. Setup your git branch on your own computer. 
2. In the root of your branch, setup a virtual environment. You can find out more for setting up a virtual environment by going to this link: https://frankcorso.dev/setting-up-python-environment-venv-requirements.html
If you name your environment something other than ```.venv``` make sure to add it to the ```.gitignore``` file. The command (on windows) is: 
    ```
    py -3 -m venv .venv 
    .venv\scripts\activate
    ``` 
3. Make sure that your virtual envrionment is set as your interpreter. If you're using Visual Studio Code you can follow this tutorial: https://code.visualstudio.com/docs/python/python-tutorial
4. Use pip to install the dependencies into your virtual environment. On Windows:
    ```
    (.venv) (path)> python -m pip install -r requirements.txt
    ```
5. Check that everything was installed correctly by running the ```test_caller.py``` file in the ```src\``` directory.