# AndroidPathPrinter
This repository contains several jython scripts for transforming images into commands that gets sent to an Android device as touch signals.

Note that `print_points.py` and `print_path.py` are Jython scripts, not Pythons scripts.

## `print_points.py`
This script reads in a png image and "draws" it on the device's screen. A color has to specified (in the code) in order to filter out pixels that should not be drawn.

## `print_path.py`
This scripts reads in an svg image, converts it to a series of commands and draws it on the device's screen. This is different than `print_points` where this prints out actual paths.

# Dependencies
- [`svg.path` 2.2](https://pypi.python.org/pypi/svg.path) 

Install with

    pip install svg.path

# Why?
This was originally developed to automate the process of drawing perfect pictures in the mobile game DrawSomething.
