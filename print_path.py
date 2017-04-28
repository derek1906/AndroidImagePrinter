# ~/Library/Android/sdk/tools/bin/monkeyrunner ~/print_path.py
import os, sys, ast

args = sys.argv[1:]
if len(args) != 1:
	print("Usage: ~/Library/Android/sdk/tools/bin/monkeyrunner print_path.py <svg_name>")
	sys.exit(1)

from com.android.monkeyrunner import MonkeyRunner, MonkeyImage, MonkeyDevice

# run svg parsing outside of Jython
print("Parsing input svg...")
input = "".join(os.popen("python path_to_points.py %s" % args[0] ))

delay = 0
data = []
for line in input.split("|"):
	parts = line.split(",")
	data.append({
		"mode": parts[0],
		"x": parts[1],
		"y": parts[2]
	})

print("Generated %d commands." % len(data))

device = MonkeyRunner.waitForConnection()

command = {
	"DOWN": (lambda x, y: device.touch(x, y, MonkeyDevice.DOWN)),
	"MOVE": (lambda x, y: device.touch(x, y, MonkeyDevice.MOVE)),
	"UP": (lambda x, y: device.touch(x, y, MonkeyDevice.UP))
}

print("Sending commands...")
for index, instruction in enumerate(data):
	command[instruction["mode"]](int(instruction["x"]), int(instruction["y"]))
	sys.stdout.write("\r")
	sys.stdout.write("Progress: %d%%" % (index * 100 / len(data)))
	sys.stdout.flush()
	MonkeyRunner.sleep(delay)
print("\rCompleted.       ")
