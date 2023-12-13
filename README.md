# Team 6 FFF Slicer

This is a class project undertaken by students at Clemson University. It's purpose is to take STL files and output GCode to a FFF (Fused Filament Fabrication, AKA FDM) printer. 

Date: Jan - Apr, 2022
Authors: William Hawthorne, John Morris

## Setup Instructions
This package is setup to be able to be installed using pip, however, it is not necessary to do so. 

Using Git:
1. Setup your git repository on your computer. This means that you'll pull all the files from here onto a folder on your computer. You can make changes to this folder, and whatever else you'd like to do. You can also choose to commit those changes back to the main branch so that everyone can see them. You can see more about using git here: https://www.freecodecamp.org/news/git-and-github-for-beginners/
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

6. If you add more dependencies to the project, make sure to run ```pip freeze > requirements.txt``` to save it to the requirements.txt file.

### To Build Project
You'll have to build the project if you want to distribute it. Building is OS specific, so it will only work on the OS of the computer you build on, but then it can be shared as an executable to anyone running that OS.

1. Make sure you have pyinstaller installed using pip.

2. Run ```pyinstaller cli.spec``` into the terminal. This will create a ```dist``` directory that will contain the single executable.

3. Note that the project will follow the path in ```cli.py```, which calls ```src/__main__.py```. So put the script you want to be run by the executable in there.