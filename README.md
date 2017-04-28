# AndroidPathPrinter
This repository contains several jython scripts for transforming images into commands that gets sent to an Android device as touch signals.

Note that `print_points.py` and `print_path.py` are Jython scripts, not Pythons scripts.

## Assumptions
This assumes the device's screen with is 1440. Adjust the code accordingly for different screen sizes.

### `print_points.py`
This script reads in a png image and "draws" it on the device's screen. A color has to specified (in the code) in order to filter out pixels that should not be drawn.

### `print_path.py`
This scripts reads in an svg image, converts it to a series of commands and draws it on the device's screen. This is different than `print_points` where this prints out actual paths.

## Dependencies
- [`MonkeyRunner`](https://developer.android.com/studio/test/monkeyrunner/index.html) from Android SDK
- [`svg.path` 2.2](https://pypi.python.org/pypi/svg.path) 

Install with

    pip install svg.path

# Restrictions
Image size cannot be larger than 144x144 for `print_points`, and width cannot exceed 1440px for `print_path`.

## How to Run
Run the scripts with MonkeyRunner.

    monkeyrunner print_path.py my_image.svg

MonkeyRunner usual locations:

- Mac: `~/Library/Android/sdk/tools/bin/monkeyrunner`
- Linux: `/usr/local/bin/sdk/tools/monkeyrunner`

## Why?
This was originally developed to automate the process of drawing perfect pictures in the mobile game DrawSomething. #JustCompSciThings

## Screenshots
<img src="https://github.com/derek1906/AndroidImagePrinter/blob/master/screenshot.png" width="500">
