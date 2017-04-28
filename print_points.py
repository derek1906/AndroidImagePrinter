# ~/Library/Android/sdk/tools/monkeyrunner ~/test.py
import sys

args = sys.argv[1:]
if len(args) != 3:
	print("Usage: ~/Library/Android/sdk/tools/bin/monkeyrunner print_points.py <image_name> <image_width> <image_height>")
	sys.exit(1)

from com.android.monkeyrunner import MonkeyRunner, MonkeyImage

device = MonkeyRunner.waitForConnection()

print("Loading image...")
img = MonkeyRunner.loadImageFromFile(args[0], "r")
color = (0, 0, 0)	# target color
gapX = 10        	# scale of the gap x
gapY = 10        	# scale of the gap y
offsetX = 5
offsetY = 500

def color_match(pixel, color):
	#return pixel[1] == color[0] and pixel[2] == color[1] and pixel[3] == color[2]
	return pixel[1] != 255 and pixel[2] != 255 and pixel[3] != 255

print("Sending commands...")
for x in range(0, int(args[1])):
	for y in range(0, int(args[2])):
		pixel = img.getRawPixel(x, y)
		if color_match(pixel, color):
			device.touch(offsetX + x * gapX, offsetY + y * gapY, 'DOWN_AND_UP')
